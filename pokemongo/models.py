# -*- coding: utf-8 -*-
import uuid
import json
import logging
logger = logging.getLogger('django.trainerdex')
import requests

from allauth.socialaccount.models import SocialAccount
from cities.models import Country, Region
from core.models import DiscordGuild, get_guild_members, DiscordRole, DiscordGuildMembership
from core.shortcuts import dict_to_choices
from collections import defaultdict
from colorful.fields import RGBColorField
from datetime import date, datetime, timedelta, timezone, time
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.postgres import fields as postgres_fields
from django.core import validators
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.db.models import Max
from django.db.models.signals import *
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, pgettext_lazy, npgettext_lazy, to_locale, get_supported_language_variant, get_language
from exclusivebooleanfield.fields import ExclusiveBooleanField
from pokemongo.validators import PokemonGoUsernameValidator, TrainerCodeValidator
from pokemongo.shortcuts import level_parser, circled_level, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, lookup, UPDATE_NON_REVERSEABLE_FIELDS, BADGES
from os.path import splitext

def VerificationImagePath(instance, filename):
    return 'v_{0}_{1}{ext}'.format(
        instance.owner.id,
        datetime.utcnow().timestamp(),
        ext=splitext(filename)[1]
        )

def VerificationUpdateImagePath(instance, filename):
    return 'v_{0}/v_{1}_{2}{ext}'.format(
        instance.trainer.owner.id,
        instance.trainer.id,
        instance.submission_date.timestamp(),
        ext=splitext(filename)[1]
        )
    
def get_path_for_badges(instance, filename):
    return f"profile/badges/{instance.slug}{splitext(filename)[1]}"

class Faction():
    def __init__(self, id: int):
        if not (0 <= id <= 3):
            raise ValueError("Must be one of four choices: 0, 1, 2, 3")
        self.id = id
        self.verbose_name = settings.TEAMS[self.id]
    
    def get_image_url(self):
        from django.contrib.staticfiles.templatetags.staticfiles import static
        return static(f'img/faction/{self.id}.png')
    
    def __str__(self):
        return str(self.verbose_name)
        
    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, Faction):
            return self.id == other.id
        else:
            raise NotImplementedError
        
    def __bool__(self):
        return True

class Trainer(models.Model):
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer',
        verbose_name=_("User"),
        )
    start_date = models.DateField(
        null=True,
        blank=True,
        validators=[MinValueValidator(date(2016, 7, 5))],
        verbose_name=pgettext_lazy("profile_start_date", "Start Date"),
        help_text=_("The date you created your Pokémon Go account."),
        )
    faction = models.SmallIntegerField(
        choices=dict_to_choices(settings.TEAMS),
        null=True,
        verbose_name=pgettext_lazy("faction", "Team"),
        )
    last_cheated = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Cheated"),
        help_text=_("When did this Trainer last cheat?"),
        )
    statistics = models.BooleanField(
        default=True,
        verbose_name=pgettext_lazy("Profile_Category_Stats", "Statistics"),
        help_text=_("Would you like to be shown on the leaderboard? Ticking this box gives us permission to process your data."),
        )
    
    daily_goal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Rate Goal"),
        help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP do you aim to gain a day?"),
        )
    total_goal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Reach Goal"),
        help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP are you aiming for next?"),
        )
    
    trainer_code = models.CharField(
        null=True,
        blank=True,
        validators=[TrainerCodeValidator],
        max_length=15,
        verbose_name=pgettext_lazy("friend_code_title", "Trainer Code"),
        help_text=_("Fancy sharing your trainer code? (Disclaimer: This information will be public)"),
        )
    
    leaderboard_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Country"),
        related_name='leaderboard_trainers_country',
        help_text=_("Where are you based?"),
        )
    leaderboard_region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Region"),
        related_name='leaderboard_trainers_region',
        help_text=_("Where are you based?"),
        )
    
    verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Modified"),
        )
    
    event_10b = models.BooleanField(
        default=False,
        )
    event_1k_users = models.BooleanField(
        default=False,
        )
    
    verification = models.ImageField(
        upload_to=VerificationImagePath,
        blank=True,
        verbose_name=_("Username / Level / Team Screenshot"),
        )
    
    def team(self):
        return Faction(int(self.faction))
    
    def has_cheated(self):
        return bool(self.last_cheated)
    has_cheated.boolean = True
    has_cheated.short_description = _("Historic Cheater")
    
    def currently_cheats(self):
        if self.last_cheated and self.last_cheated+timedelta(weeks=26) > timezone.now().date():
            return True
        else:
            return False
    currently_cheats.boolean = True
    currently_cheats.short_description = _("Cheater")
    
    def is_prefered(self):
        return True
    
    def flag_emoji(self):
        if self.leaderboard_country:
            return lookup(self.leaderboard_country.code)
        else:
            return None
    
    def submitted_picture(self):
        return bool(self.verification)
    submitted_picture.boolean = True
    
    def awaiting_verification(self):
        if bool(self.verification) is True and bool(self.verified) is False:
            return True
        return False
    awaiting_verification.boolean = True
    awaiting_verification.short_description = _("Ready to be verified!")
    
    def is_verified(self):
        return self.verified
    is_verified.boolean = True
    is_verified.short_description = _("Verified")
    
    def is_verified_and_saved(self):
        return bool(bool(self.verified) and bool(self.verification))
    is_verified_and_saved.boolean = True
    
    def is_on_leaderboard(self):
        return bool(self.is_verified and self.statistics and not self.currently_cheats())
    is_on_leaderboard.boolean = True
    
    def level(self):
        updates = self.update_set.exclude(total_xp__isnull=True)
        if updates.exists():
            return updates.latest('update_time').level()
        return None
    
    @property
    def active(self):
        return self.owner.is_active
    
    @property
    def profile_complete(self):
        return bool(
            bool(self.owner) and bool(self.username) and bool(bool(self.verification) or bool(self.verified)) and bool(self.start_date)
        )
    
    @property
    def profile_completed_optional(self):
        return self.profile_complete
    
    @property
    def nickname(self):
        """Gets nickname, fallback to User username"""
        try:
            return self.nickname_set.get(active=True).nickname
        except Nickname.DoesNotExist:
            return self.user.username
    
    @property
    def username(self):
        """Alias for nickname"""
        return self.nickname
    
    def __str__(self):
        return self.nickname
    
    def get_absolute_url(self):
        return reverse('trainerdex:profile_nickname', kwargs={'nickname':self.nickname})
    
    class Meta:
        verbose_name = _("Trainer")
        verbose_name_plural = _("Trainers")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        trainer = Trainer.objects.create(owner=kwargs['instance'])
        return trainer
    return None

class Nickname(models.Model):
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=pgettext_lazy("player_term", "Trainer"),
        )
    nickname = postgres_fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        db_index=True,
        verbose_name=pgettext_lazy("onboard_enter_name_hint", "Nickname"),
        )
    active = ExclusiveBooleanField(
        on='trainer',
        )
    
    def clean(self):
        if self.active and self.trainer.owner.username != self.nickname:
            self.trainer.owner.username = self.nickname
            self.trainer.owner.save()
        
    def __str__(self):
        return self.nickname
        
    class Meta:
        ordering = ['nickname']

@receiver(post_save, sender=Trainer)
def new_trainer_set_nickname(sender, **kwargs):
    if kwargs['created']:
        nickname = Nickname.objects.create(
            trainer=kwargs['instance'],
            nickname=kwargs['instance'].owner.username,
            active=True
            )
        return nickname
    return None

class Update(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
        )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        verbose_name=_("Trainer"),
        )
    update_time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Time Updated"),
        )
    
    DATABASE_SOURCES = (
        ('?', None),
        ('cs_social_twitter', 'Twitter (Found)'),
        ('cs_social_facebook', 'Facebook (Found)'),
        ('cs_social_youtube', 'YouTube (Found)'),
        ('cs_?', 'Sourced Elsewhere'),
        ('ts_social_discord', 'Discord'),
        ('ts_social_twitter', 'Twitter'),
        ('ts_direct', 'Directly told (via text)'),
        ('web_quick', 'Quick Update (Web)'),
        ('web_detailed', 'Detailed Update (Web)'),
        ('ts_registration', 'Registration'),
        ('ss_registration', 'Registration w/ Screenshot'),
        ('ss_generic', 'Generic Screenshot'),
        ('ss_ocr', "OCR Screenshot"),
        ('com.nianticlabs.pokemongo.friends', "In Game Friends"),
        ('com.pokeassistant.trainerstats', "Poké Assistant"),
        ('com.pokenavbot.profiles', "PokeNav"),
        ('tl40datateam.spreadsheet', "Tl40 Data Team (Legacy)"),
        ('com.tl40data.website', "Tl40 Data Team"),
        ('com.pkmngots.import', "Third Saturday"),
    )
    
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submission Datetime"),
        )
    data_source = models.CharField(
        max_length=256,
        choices=DATABASE_SOURCES,
        default='?',
        verbose_name=_("Source"),
        )
    screenshot = models.ImageField(
        upload_to=VerificationUpdateImagePath,
        blank=True,
        verbose_name=_("Screenshot"),
        help_text=_("This should be your TOTAL XP screenshot."),
        )
    
    # Error Override Checks
    double_check_confirmation = models.BooleanField(
        default=False,
        verbose_name=_("I have double checked this information and it is correct."),
        help_text=_("This will silence some errors."),
        )
    
    # Can be seen on main profile
    total_xp = models.PositiveIntegerField(
        null=True, # Are you sure you want this?
        verbose_name=pgettext_lazy("PROFILE_TOTAL_XP", "Total XP"),
        )
    
    # Pokedex Figures
    pokedex_caught = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_page_caught", "Unique Species Caught"),
        )
    pokedex_seen = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_page_seen", "Unique Species Seen"),
        )
    
    # Medals
    badge_travel_km = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_travel_km_title", "Jogger"),
        help_text=pgettext_lazy("badge_travel_km", "Walk {0:0,g} km").format(1000.0),
        )
    badge_pokedex_entries = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_title", "Kanto"),
        help_text=pgettext_lazy("badge_pokedex_entries", "Register {0} Kanto region Pokémon in the Pokédex.").format(100),
        validators=[MaxValueValidator(151)],
        )
    badge_capture_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_capture_total_title", "Collector"),
        help_text=pgettext_lazy("badge_capture_total", "Catch {0} Pokémon.").format(2000),
        )
    badge_evolved_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_evolved_total_title", "Scientist"),
        help_text=pgettext_lazy("badge_evolved_total", "Evolve {0} Pokémon.").format(200),
        )
    badge_hatched_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_hatched_total_title", "Breeder"),
        help_text=pgettext_lazy("badge_hatched_total", "Hatch {0} eggs.").format(500),
        )
    badge_pokestops_visited = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokestops_visited_title", "Backpacker"),
        help_text=pgettext_lazy("badge_pokestops_visited", "Visit {0} PokéStops.").format(2000),
        )
    badge_big_magikarp = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_big_magikarp_title", "Fisherman"),
        help_text=pgettext_lazy("badge_big_magikarp", "Catch {0} big Magikarp.").format(300),
        )
    badge_battle_attack_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_battle_attack_won_title", "Battle Girl"),
        help_text=pgettext_lazy("badge_battle_attack_won", "Win {0} Gym battles.").format(1000),
        )
    badge_battle_training_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_battle_training_won_title", "Ace Trainer"),
        help_text=pgettext_lazy("badge_battle_training_won", "Train {0} times.").format(1000),
        )
    badge_small_rattata = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_small_rattata_title", "Youngster"),
        help_text=pgettext_lazy("badge_small_rattata", "Catch {0} tiny Rattata.").format(300),
        )
    badge_pikachu = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pikachu_title", "Pikachu Fan"),
        help_text=pgettext_lazy("badge_pikachu", "Catch {0} Pikachu.").format(300),
        )
    badge_unown = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_unown_title", "Unown"),
        help_text=pgettext_lazy("badge_unown", "Catch {0} Unown.").format(26),
        validators=[MaxValueValidator(28)],
        )
    badge_pokedex_entries_gen2 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen2_title", "Johto"),
        help_text=pgettext_lazy("badge_pokedex_entries_gen2", "Register {0} Pokémon first discovered in the Johto region to the Pokédex.").format(70),
        validators=[MaxValueValidator(100)],
        )
    badge_raid_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_raid_battle_won_title", "Champion"),
        help_text=pgettext_lazy("badge_raid_battle_won", "Win {0} Raids.").format(1000),
        )
    badge_legendary_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_legendary_battle_won_title", "Battle Legend"),
        help_text=pgettext_lazy("badge_legendary_battle_won", "Win {0} Legendary Raids.").format(1000),
        )
    badge_berries_fed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_berries_fed_title", "Berry Master"),
        help_text=pgettext_lazy("badge_berries_fed", "Feed {0} Berries at Gyms.").format(1000),
        )
    badge_hours_defended = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_hours_defended_title", "Gym Leader"),
        help_text=pgettext_lazy("badge_hours_defended", "Defend Gyms for {0} hours.").format(1000),
        )
    badge_pokedex_entries_gen3 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen3_title", "Hoenn"),
        help_text=pgettext_lazy("badge_pokedex_entries_gen3", "Register {0} Pokémon first discovered in the Hoenn region to the Pokédex.").format(90),
        validators=[MaxValueValidator(133)],
        )
    badge_challenge_quests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_challenge_quests_title", "Pokémon Ranger"),
        help_text=pgettext_lazy("badge_challenge_quests", "Complete {0} Field Research tasks.").format(1000),
        )
    badge_max_level_friends = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_max_level_friends_title", "Idol"),
        help_text=pgettext_lazy("badge_max_level_friends", "Become Best Friends with {0} Trainers.").format(3),
        validators=[MaxValueValidator(200)],
        )
    badge_trading = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_trading_title", "Gentleman"),
        help_text=pgettext_lazy("badge_trading", "Trade {0} Pokémon.").format(1000),
        )
    badge_trading_distance = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_trading_distance_title", "Pilot"),
        help_text=pgettext_lazy("badge_trading_distance", "Earn {0} km across the distance of all Pokémon trades.").format(1000000),
        )
    badge_pokedex_entries_gen4 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen4__title", "Sinnoh"),
        help_text=pgettext_lazy("badge_pokedex_entries_gen4__help", "Register {0} Pokémon first discovered in the Sinnoh region to the Pokédex.").format(80),
        validators=[MaxValueValidator(99)],
        )
    
    badge_great_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_great_league_title", "Great League Veteran"),
        help_text=pgettext_lazy("badge_great_league", "Win {} Trainer Battles in the Great League.").format(200),
        )
    badge_ultra_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_ultra_league_title", "Ultra League Veteran"),
        help_text=pgettext_lazy("badge_ultra_league", "Win {} Trainer Battles in the Ultra League.").format(200),
        )
    badge_master_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_master_league_title", "Master League Veteran"),
        help_text=pgettext_lazy("badge_master_league", "Win {} Trainer Battles in the Master League.").format(200),
        )
    badge_photobomb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_photobomb_title", "Cameraman"),
        help_text=npgettext_lazy("badge_photobomb", "Have {0} surprise encounter in AR Snapshot.", "Have {0} surprise encounters in AR Snapshot.", 2).format(200),
        )
    
    badge_pokedex_entries_unknown = models.PositiveIntegerField( # Meltan Generation, assumed to be Gen 8
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_unknown_title", "Unknown Generation"),
        help_text=pgettext_lazy("badge_pokedex_entries_unknown", "This is the Unknown generation at the end of your Pokédex with Meltan and Melmetal."),
        validators=[MaxValueValidator(2)],
        )
    
    badge_type_normal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_normal_title", "Schoolkid"),
        help_text=pgettext_lazy("badge_type_normal", "Catch {0} Normal-type Pokémon").format(200),
        )
    badge_type_fighting = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fighting_title", "Black Belt"),
        help_text=pgettext_lazy("badge_type_fighting", "Catch {0} Fighting-type Pokémon").format(200),
        )
    badge_type_flying = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_flying_title", "Bird Keeper"),
        help_text=pgettext_lazy("badge_type_flying", "Catch {0} Flying-type Pokémon").format(200),
        )
    badge_type_poison = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_poison_title", "Punk Girl"),
        help_text=pgettext_lazy("badge_type_poison", "Catch {0} Poison-type Pokémon").format(200),
        )
    badge_type_ground = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ground_title", "Ruin Maniac"),
        help_text=pgettext_lazy("badge_type_ground", "Catch {0} Ground-type Pokémon").format(200),
        )
    badge_type_rock = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_rock_title", "Hiker"),
        help_text=pgettext_lazy("badge_type_rock", "Catch {0} Rock-type Pokémon").format(200),
        )
    badge_type_bug = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_bug_title", "Bug Catcher"),
        help_text=pgettext_lazy("badge_type_bug", "Catch {0} Bug-type Pokémon").format(200),
        )
    badge_type_ghost = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ghost_title", "Hex Maniac"),
        help_text=pgettext_lazy("badge_type_ghost", "Catch {0} Ghost-type Pokémon").format(200),
        )
    badge_type_steel = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_steel_title", "Depot Agent"),
        help_text=pgettext_lazy("badge_type_steel", "Catch {0} Steel-type Pokémon").format(200),
        )
    badge_type_fire = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fire_title", "Kindler"),
        help_text=pgettext_lazy("badge_type_fire", "Catch {0} Fire-type Pokémon").format(200),
        )
    badge_type_water = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_water_title", "Swimmer"),
        help_text=pgettext_lazy("badge_type_water", "Catch {0} Water-type Pokémon").format(200),
        )
    badge_type_grass = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_grass_title", "Gardener"),
        help_text=pgettext_lazy("badge_type_grass", "Catch {0} Grass-type Pokémon").format(200),
        )
    badge_type_electric = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_electric_title", "Rocker"),
        help_text=pgettext_lazy("badge_type_electric", "Catch {0} Electric-type Pokémon").format(200),
        )
    badge_type_psychic = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_psychic_title", "Psychic"),
        help_text=pgettext_lazy("badge_type_psychic", "Catch {0} Pychic-type Pokémon").format(200),
        )
    badge_type_ice = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ice_title", "Skier"),
        help_text=pgettext_lazy("badge_type_ice", "Catch {0} Ice-type Pokémon").format(200),
        )
    badge_type_dragon = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_dragon_title", "Dragon Tamer"),
        help_text=pgettext_lazy("badge_type_dragon", "Catch {0} Dragon-type Pokémon").format(200),
        )
    badge_type_dark = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_dark_title", "Delinquent"),
        help_text=pgettext_lazy("badge_type_dark", "Catch {0} Dark-type Pokémon").format(200),
        )
    badge_type_fairy = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fairy_title", "Fairy Tale Girl"),
        help_text=pgettext_lazy("badge_type_fairy", "Catch {0} Fairy-type Pokémon").format(200),
        )
    
    # Extra Questions
    gymbadges_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("gymbadges_total", "Gym Badges"),
        validators=[MaxValueValidator(1000)],
        )
    gymbadges_gold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("gymbadges_gold", "Gold Gym Badges"),
        validators=[MaxValueValidator(1000)],
        )
    pokemon_info_stardust = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokemon_info_stardust_label", "Stardust"),
        )
    
    def level(self):
        if self.total_xp:
            return level_parser(xp=self.total_xp).level
        return None
    
    def __str__(self):
        return _("Update(trainer: {trainer}, update_time: {time}, {stats})").format(
            trainer=self.trainer,
            time=self.update_time,
            stats=','.join([f'{x}: {getattr(self, x)}' for x in self.modified_fields()]),
            )
    
    def has_modified_extra_fields(self):
        return bool(self.modified_extra_fields())
    has_modified_extra_fields.boolean = True

    def modified_fields(self):
        return [x for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('pokedex_caught', 'pokedex_seen', 'gymbadges_total', 'gymbadges_gold', 'pokemon_info_stardust', 'total_xp')) if getattr(self, x)]
    
    def modified_extra_fields(self):
        return [x for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('pokedex_caught', 'pokedex_seen', 'gymbadges_total', 'gymbadges_gold', 'pokemon_info_stardust')) if getattr(self, x)]
    
    def clean(self):
        if not self.trainer:
            return
        
        hard_error_dict = defaultdict(list)
        soft_error_dict = defaultdict(list)
        
        # Hard Coded Dates
        LaunchDate = date(2016,7,6)
        DittoDate = date(2016,11,22)
        Gen2Date = date(2017,2,10)
        Gen3Date = date(2017,10,20)
        GymCloseDate = date(2017,6,19)
        GymReworkDate = date(2017,6,22)
        RaidReleaseDate = date(2017,6,26)
        LegendaryReleaseDate = date(2017,7,22)
        ShinyReleaseDate = date(2017,3,25)
        QuestReleaseDate = date(2018,3,30)
        FriendReleaseDate = date(2018,6,21)
        Gen4Date = date(2018,10,16)
        PVPDate = date(2018,12,13)
            
        for field in Update._meta.get_fields():
            if bool(getattr(self, field.name)):
                # Get latest update with that field present, only get the important fields.
                last_update = self.trainer.update_set.filter(update_time__lt=self.update_time) \
                    .exclude(**{field.name : None}) \
                    .order_by('-'+field.name, '-update_time') \
                    .only(field.name, 'update_time') \
                    .first()
                
                # Overall Rules
                
                # 1 - Value must be higher than or equal to than previous value
                if bool(last_update) and field.name in UPDATE_NON_REVERSEABLE_FIELDS:
                    if getattr(self, field.name) < getattr(last_update, field.name):
                        hard_error_dict[field.name].append(ValidationError(_("This value has previously been entered at a higher value. Please try again ensuring the value you entered was correct.")))
                
                # 2 - Value should less than 1.5 times higher than the leader
                if bool(last_update) and field.name in UPDATE_NON_REVERSEABLE_FIELDS:
                    leading_value = getattr(Update.objects.order_by(f'-{field.name}').only(field.name).first(), field.name)
                    if bool(leading_value):
                        print('comparing', field.name, getattr(self, field.name), leading_value)
                        if getattr(self, field.name) > (leading_value * Decimal('1.5')):
                            soft_error_dict[field.name].append(ValidationError(_("This value will make you the leader. Are you sure what you entered is correct?")))
                    else:
                        pass
                
                # Field specific Validation
                
                # 1 - total_xp - Total XP
                if field.name == 'total_xp':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 1M
                    DailyLimit = 10000000
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 2 - badge_travel_km - Jogger
                if field.name == 'badge_travel_km':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 60
                    DailyLimit = Decimal('60.0')
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / Decimal(str(_timedelta.total_seconds()/86400))
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / Decimal(str(_timedelta.total_seconds()/86400)) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 3 - badge_pokedex_entries - Kanto
                if field.name == 'badge_pokedex_entries':
                    
                    # Max Value = 151
                    # Handled at field level
                    pass
                
                # 4 - badge_capture_total - Collector
                if field.name == 'badge_capture_total':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 800
                    DailyLimit = 800
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 5 - badge_evolved_total - Scientist
                if field.name == 'badge_evolved_total':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 250
                    DailyLimit = 250
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 6 - badge_hatched_total - Breeder
                if field.name == 'badge_hatched_total':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 60
                    DailyLimit = 60
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 7 - badge_pokestops_visited - Backpacker
                if field.name == 'badge_pokestops_visited':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 500
                    DailyLimit = 500
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 8 - badge_big_magikarp - Fisherman
                if field.name == 'badge_big_magikarp':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 25
                    DailyLimit = 25
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 9 - badge_battle_attack_won - Battle Girl
                if field.name == 'badge_battle_attack_won':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 500
                    DailyLimit = 500
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 10 - badge_battle_training_won - Ace Trainer
                if field.name == 'badge_battle_training_won':
                    
                    # InterestDate = StartDate
                    InterestDate = PVPDate
                    # DailyLimit = 25
                    DailyLimit = 100
    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                    
                    if GymCloseDate < self.update_time.date() < PVPDate : # If update is when Ace Trainer was closed, clear it.
                        setattr(self,field.name, None)
                
                # 11 - badge_small_rattata - Youngster
                if field.name == 'badge_small_rattata':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 25
                    DailyLimit = 25
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 12 - badge_pikachu - Pikachu Fan
                if field.name == 'badge_pikachu':
                    
                    # InterestDate = StartDate
                    InterestDate = self.trainer.start_date
                    # DailyLimit = 100
                    DailyLimit = 100
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                
                # 13 - badge_berries_fed - Berry Master
                if field.name == 'badge_berries_fed':
                    
                    # InterestDate = Max(GymReworkDate, StartDate)
                    InterestDate = max(GymReworkDate, self.trainer.start_date)
                    # DailyLimit = 3200
                    DailyLimit = 3200
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < GymReworkDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=GymReworkDate)))
                
                # 14 - badge_pokedex_entries_gen2 - Johto
                if field.name == 'badge_pokedex_entries_gen2':
                    
                    # Max Value = 99
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < Gen2Date:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=Gen2Date)))
                
                # 15 - badge_hours_defended - Gym Leader
                if field.name == 'badge_hours_defended':
                    
                    # InterestDate = Max(GymReworkDate, StartDate)
                    InterestDate = max(GymReworkDate, self.trainer.start_date)
                    # DailyLimit = 480
                    DailyLimit = 480
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < GymReworkDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=GymReworkDate)))
                
                # 16 - badge_unown - Unown
                if field.name == 'badge_unown':
                    
                    # Max Value = 28
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < Gen2Date:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=Gen2Date)))
                
                # 17 - badge_raid_battle_won - Champion
                if field.name == 'badge_raid_battle_won':
                    
                    # InterestDate = Max(RaidReleaseDate, StartDate)
                    InterestDate = max(RaidReleaseDate, self.trainer.start_date)
                    # DailyLimit = 100
                    DailyLimit = 100
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < RaidReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=RaidReleaseDate)))
                
                # 17 - badge_legendary_battle_won - Champion
                if field.name == 'badge_legendary_battle_won':
                    
                    # InterestDate = Max(LegendaryReleaseDate, StartDate)
                    InterestDate = max(LegendaryReleaseDate, self.trainer.start_date)
                    # DailyLimit = 100
                    DailyLimit = 100
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < LegendaryReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=LegendaryReleaseDate)))
                
                # 19 - gymbadges_gold - Gold Gyms
                if field.name == 'gymbadges_gold':
                    
                    # Max Value = 1000
                    # Handled at field level
                    
                    _xcompare = self.gymbadges_total
                    # Check if gymbadges_total is filled in
                    if _xcompare:
                        # GoldGyms < GymsSeen
                        # Check if gymbadges_gold is more of less than gymbadges_total
                        if getattr(self,field.name) > _xcompare:
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is too high. Please check for typos and other mistakes. You can't have more gold gyms than gyms in Total. {value:,}/{expected:,}").format(badge=field.verbose_name, value=getattr(self,field.name), expected=_xcompare)))
                    else:
                        hard_error_dict[field.name].append(ValidationError(_("You must fill in {other_badge} if filling in {this_badge}.").format(this_badge=field.verbose_name, other_badge=Update._meta.get_field('gymbadges_total').verbose_name)))
                
                    # Handle Early Updates
                    if self.update_time.date() < GymReworkDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=GymReworkDate)))
                    
                # 20 - gymbadges_total - Gyms Seen
                if field.name == 'gymbadges_total':
                    
                    # Max Value = 1000
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < GymReworkDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=GymReworkDate)))
                
                # 21 - badge_pokedex_entries_gen3 - Hoenn
                if field.name == 'badge_pokedex_entries_gen3':
                    
                    # Max Value = 130
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < Gen3Date:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=Gen3Date)))
                
                # 22 - badge_challenge_quests - Ranger
                if field.name == 'badge_challenge_quests':
                    
                    # InterestDate = Max(QuestReleaseDate, StartDate)
                    InterestDate = max(QuestReleaseDate, self.trainer.start_date)
                    # DailyLimit = 500
                    DailyLimit = 500
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < QuestReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=QuestReleaseDate)))
                
                # 23 - badge_max_level_friends - Idol
                if field.name == 'badge_max_level_friends':
                    
                    # Max Value = 200
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < FriendReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=FriendReleaseDate)))
                
                # 24 - badge_trading - Gentleman
                if field.name == 'badge_trading':
                    
                    # InterestDate = Max(FriendReleaseDate, StartDate)
                    InterestDate = max(FriendReleaseDate, self.trainer.start_date)
                    # DailyLimit = 100
                    DailyLimit = 100
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    # Handle Early Updates
                    if self.update_time.date() < FriendReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=FriendReleaseDate)))
                
                #24 - badge_trading_distance - Pilot
                if field.name == 'badge_trading_distance':
                    
                    # InterestDate = Max(FriendReleaseDate, StartDate)
                    InterestDate = max(FriendReleaseDate, self.trainer.start_date)
                    # DailyLimit = 1.92M
                    DailyLimit = 1920000
                    
                    # Checks Daily Limit between now and InterestDate
                    if InterestDate:
                        _timedelta = self.update_time.date()-InterestDate
                        _xdelta = getattr(self, field.name) / (_timedelta.total_seconds()/86400)
                        if _xdelta >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=InterestDate, date2=self.update_time.date())))
                    
                    # Checks Daily Limit between now and last_update
                    if bool(last_update):
                        _xdelta = getattr(self,field.name)-getattr(last_update, field.name)
                        _timedelta = self.update_time-last_update.update_time
                        if _xdelta / (_timedelta.total_seconds()/86400) >= DailyLimit:
                            # Failed Verification, raise error!
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is high. Please check for typos and other mistakes. {delta:,}/{expected:,} per day from {date1} to {date2}").format(badge=field.verbose_name, delta=_xdelta, expected=DailyLimit, date1=last_update.update_time, date2=self.update_time.date())))
                            
                    _xcompare = self.badge_trading or self.trainer.update_set.filter(update_time__lt=self.update_time).exclude(**{'badge_trading' : None}).order_by('-badge_trading', '-update_time').only('badge_trading', 'update_time').first().badge_trading
                    # Check if gymbadges_total is filled in, or has been filled in in the past
                    if _xcompare:
                        # Pilot / Gentleman < 19200
                        if (getattr(self,field.name) / _xcompare) >= 19200:
                            soft_error_dict[field.name].append(ValidationError(_("The {badge} you entered is too high. Please check for typos and other mistakes. You can only gain so much in a day. {value:,}/{expected:,}").format(badge=field.verbose_name, value=getattr(self,field.name), expected=19200)))
                
                    # Handle Early Updates
                    if self.update_time.date() < FriendReleaseDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=FriendReleaseDate)))
                
                # 25 - badge_pokedex_entries_gen4 - Sinnoh
                if field.name == 'badge_pokedex_entries_gen4':
                    
                    # Max Value = 107
                    # Handled at field level
                    
                    # Handle Early Updates
                    if self.update_time.date() < Gen3Date:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=Gen4Date)))
                
                # 25 - badge_great_league - Great League Veteran
                if field.name == 'badge_great_league':
                    
                    # Handle Early Updates
                    if self.update_time.date() < PVPDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=PVPDate)))
                
                # 25 - badge_ultra_league - Ultra League Veteran
                if field.name == 'badge_ultra_league':
                    
                    # Handle Early Updates
                    if self.update_time.date() < PVPDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=PVPDate)))
                
                # 25 - badge_master_league - Master League Veteran
                if field.name == 'badge_master_league':
                    
                    # Handle Early Updates
                    if self.update_time.date() < PVPDate:
                        hard_error_dict[field.name].append(ValidationError(_("You entered {badge} for a date before it's release. {value:,}/{expected:,}").format(badge=field.verbose_name, delta=self.update_time.date(), expected=PVPDate)))
                
        # Raise Soft Errors
        soft_error_override = any([bool(self.double_check_confirmation),('ss_' in self.data_source)])
        if soft_error_dict != {} and not soft_error_override:
            raise ValidationError(soft_error_dict)
        
        # Raise Hard Errors
        if hard_error_dict:
            raise ValidationError(hard_error_dict)
    
    class Meta:
        get_latest_by = 'update_time'
        ordering = ['-update_time']
        verbose_name = _("Update")
        verbose_name_plural = _("Updates")

@receiver(post_save, sender=Update)
def update_discord_level(sender, **kwargs):
    if kwargs['created'] and kwargs['instance'].total_xp:
        level = kwargs['instance'].level()
        for discord in DiscordGuildMembership.objects.exclude(active=False).filter(guild__settings_pokemongo_rename=True, guild__settings_pokemongo_rename_with_level=True, user__user__trainer=kwargs['instance'].trainer):
            if discord.nick_override:
                base = discord.nick_override
            else:
                base = kwargs['instance'].trainer.nickname
            
            if discord.guild.settings_pokemongo_rename_with_level_format=='int':
                ext = str(level)
            elif discord.guild.settings_pokemongo_rename_with_level_format=='circled_level':
                ext = circled_level(level)
            
            if len(base)+len(ext) > 32:
                chopped_base = base[slice(0,32-len(ext)-1)]
                combined = f"{chopped_base}…{ext}"
            elif len(base)+len(ext) == 32:
                combined = f"{base}{ext}"
            else:
                combined = f"{base} {ext}"
            
            discord._change_nick(combined)

class ProfileBadge(models.Model):
    slug = models.SlugField(
        db_index=True,
        primary_key=True,
        )
    title = models.CharField(
        db_index=True,
        max_length=20,
        )
    description = models.CharField(
        db_index=True,
        max_length=240,
        )
    badge = models.ImageField(
        upload_to=get_path_for_badges,
        )
    members = models.ManyToManyField(
        Trainer,
        through='ProfileBadgeHoldership',
        through_fields=('badge', 'trainer'),
        )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")
        
class ProfileBadgeHoldership(models.Model):
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        )
    badge = models.ForeignKey(
        ProfileBadge,
        on_delete=models.CASCADE,
        )
    awarded_by = models.ForeignKey(
        Trainer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='badges_awarded',
        )
    awarded_on = models.DateTimeField(
        auto_now_add=True,
        )
    reason_given = models.CharField(
        max_length=64,
        )
    
    def __str__(self):
        return f"{self.trainer} - {self.badge}"

class Community(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
        )
    language = models.CharField(
        max_length=12,
        choices=settings.LANGUAGES,
        )
    name = models.CharField(
        max_length=70,
        )
    description = models.TextField(
        null=True,
        blank=True,
        )
    handle = models.SlugField(
        unique=True,
        )

    privacy_public = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Viewable"),
        help_text=_("By default, this is off. Turn this on to share your community with the world."),
        )
    privacy_public_join = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Joinable"),
        help_text=_("By default, this is off. Turn this on to make your community free to join. No invites required."),
        )
    privacy_tournaments = models.BooleanField(
        default=False,
        verbose_name=_("Tournament: Publicly Viewable"),
        help_text=_("By default, this is off. Turn this on to share your tournament results with the world."),
        )

    memberships_personal = models.ManyToManyField(
        Trainer,
        blank=True,
        )
    memberships_discord = models.ManyToManyField(
        DiscordGuild,
        through='CommunityMembershipDiscord',
        through_fields=('community', 'discord'),
        blank=True,
        )

    def __str__(self):
        return self.name
    
    def get_members(self):
        qs = self.memberships_personal.all()
        
        for x in CommunityMembershipDiscord.objects.filter(sync_members=True, community=self):
            qs |= x.members_queryset()
        
        return qs
    
    def get_absolute_url(self):
        return reverse('trainerdex:leaderboard', kwargs={'community':self.handle})
    
    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")

class CommunityMembershipDiscord(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        )
    discord = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        )
    
    sync_members = models.BooleanField(
        default=True,
        help_text=_("Members in this Discord are automatically included in the community."),
        )
    include_roles = models.ManyToManyField(
        DiscordRole,
        related_name='include_roles_community_membership_discord',
        blank=True,
        )
    exclude_roles = models.ManyToManyField(
        DiscordRole,
        related_name='exclude_roles_community_membership_discord',
        blank=True,
        )

    def __str__(self):
        return "{community} - {guild}".format(community=self.community, guild=self.discord)
    
    def members_queryset(self):
        if self.sync_members:
            qs =  Trainer.objects.exclude(owner__is_active=False) \
                .filter(owner__socialaccount__discordguildmembership__guild__communitymembershipdiscord=self)
            
            if self.include_roles.exists():
                q = models.Q()
                for role in self.include_roles.all():
                    q = q | models.Q(owner__socialaccount__discordguildmembership__data__roles__contains=str(role.id))
                qs = qs.filter(q)
            
            if self.exclude_roles.exists():
                q = models.Q()
                for role in self.exclude_roles.all():
                    q = q | models.Q(owner__socialaccount__discordguildmembership__data__roles__contains=str(role.id))
                qs = qs.exclude(q)
            
            return qs
        else:
            return Trainer.objects.none()

    class Meta:
        verbose_name = _("Community Discord Connection")
        verbose_name_plural = _("Community Discord Connections")
