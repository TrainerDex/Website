import json
import logging
import uuid

import datetime
from collections import defaultdict
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, pgettext_lazy, pgettext
from django_countries.fields import CountryField

from core.models import Nickname, User
# from core.models import DiscordGuildMembership
from trainerdex.validators import PokemonGoUsernameValidator, TrainerCodeValidator
from trainerdex.shortcuts import circled_level
from trainerdex.shortcuts import BADGES, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_POKEDEX, UPDATE_FIELDS_TYPES, UPDATE_NON_REVERSEABLE_FIELDS

log = logging.getLogger('django.trainerdex')


class Trainer(models.Model):
    """The model used to represent a users profile in the database"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer',
        verbose_name=pgettext_lazy("profile__user__title", "User"),
        primary_key=True,
        )
    id = models.PositiveIntegerField(
        editable= False,
        verbose_name='(Deprecated) ID',
        blank=True,
        null=True,
        )
    start_date = models.DateField(
        null=True,
        blank=False,
        validators=[MinValueValidator(datetime.date(2016, 7, 5))],
        verbose_name=pgettext_lazy("profile__start_date__title", "Start Date"),
        help_text=pgettext_lazy("profile__start_date__help", "The date you created your Pokémon Go account. This can be found under TOTAL ACTIVITY in-game."),
        )
    faction = models.ForeignKey(
        'Faction',
        on_delete=models.PROTECT,
        verbose_name=pgettext_lazy("profile__faction__title", "Team"),
        default=0,
        )
    
    trainer_code = models.CharField(
        null=True,
        blank=True,
        validators=[TrainerCodeValidator],
        max_length=15,
        verbose_name=pgettext_lazy("profile__friend_code__title", "Trainer Code"),
        help_text=pgettext_lazy("profile__friend_code__help", "Fancy sharing your trainer code?"),
        )
    
    country = CountryField()
    
    verified = models.BooleanField(
        default=False,
        verbose_name=pgettext_lazy("profile__verified__title", "Verified"),
        )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=pgettext_lazy("profile__last_modified__title", "Last Modified"),
        )
    
    # verification_image = models.ImageField(
    #     upload_to=verification_image_path,
    #     blank=True,
    #     verbose_name=pgettext_lazy("profile__verification_image__title", "In-Game Profile Screenshot"),
    #     )
    
        
    banned = models.BooleanField(
        default=False,
        verbose_name=_("Banned"),
        )

    def submitted_picture(self) -> bool:
        # return bool(self.verification_image)
        return False
    submitted_picture.boolean = True
    
    def awaiting_verification(self) -> bool:
        return (self.submitted_picture() and not self.verified)
    awaiting_verification.boolean = True
    awaiting_verification.short_description = pgettext_lazy("profile__awaiting_verification__description", "Ready to be verified!")
    
    @property
    def leaderboard_eligibility_detail(self) -> dict:
        """Returns if a user is eligibile for the leaderboard"""
        return {
            'verified': self.verified,
            'gdpr': self.user.gdpr,
            'not_banned': not self.banned,
        }
    
    def leaderboard_eligibility(self) -> bool:
        return all(self.leaderboard_eligibility_detail.values())
    leaderboard_eligibility.boolean = True
    
    @property
    def profile_complete(self) -> bool:
        # return all([self.user, self.nickname, self.submitted_picture(), self.verified, self.start_date])
        return all([self.user, self.nickname, self.verified, self.start_date])
    
    @property
    def nickname(self) -> str:
        """Gets nickname, fallback to User.username"""
        try:
            return self.user.nickname_set.get(active=True).nickname
        except Nickname.DoesNotExist:
            return self.user.username
    
    @property
    def username(self) -> str:
        """Alias for nickname"""
        return self.nickname
    
    def __str__(self):
        return self.nickname
    
    def get_absolute_url(self) -> str:
        return reverse('trainerdex:profile_nickname', kwargs={'nickname':self.nickname})
    
    class Meta:
        verbose_name = _("Trainer")
        verbose_name_plural = _("Trainers")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs) -> Trainer:
    if kwargs.get('raw'):
        # End early, one should not query/modify other records in the database as the database might not be in a consistent state yet.
        return None
    
    if instance.is_service_user:
        # End early, service users shouldn't have Trainer objects
        return None
    
    if created:
        return Trainer.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    if kwargs.get('raw'):
        # End early, one should not query/modify other records in the database as the database might not be in a consistent state yet.
        return None
    
    if instance.is_service_user:
        # End early, service users shouldn't have Trainer objects
        return None
    
    try:
        instance.trainer.save()
    except User.trainer.RelatedObjectDoesNotExist:
        pass


class Faction(models.Model):
    """
    Managed by the system, automatically created via a Django data migration
    """
    TEAMLESS = 0
    MYSTIC = 1
    VALOR = 2
    INSTINCT = 3
    FACTION_CHOICES = (
        (TEAMLESS, pgettext('faction_0__short', 'Teamless')),
        (MYSTIC, pgettext('faction_1__short', 'Mystic')),
        (VALOR, pgettext('faction_2__short', 'Valor')),
        (INSTINCT, pgettext('faction_3__short', 'Instinct')),
    )
    
    id = models.PositiveSmallIntegerField(choices=FACTION_CHOICES, primary_key=True)
    
    @property
    def name_short(self):
        CHOICES = (
        pgettext('faction_0__short', 'Teamless'),
        pgettext('faction_1__short', 'Mystic'),
        pgettext('faction_2__short', 'Valor'),
        pgettext('faction_3__short', 'Instinct'),
        )
        return CHOICES[self.id]
    
    @property
    def name_long(self):
        CHOICES = (
        pgettext('faction_0__long', 'No Team'),
        pgettext('faction_1__long', 'Team Mystic'),
        pgettext('faction_2__long', 'Team Valor'),
        pgettext('faction_3__long', 'Team Instinct'),
        )
        return CHOICES[self.id]
    
    
    def __str__(self):
        return self.name_short


class Update(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
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
    # screenshot = models.ImageField(
    #     upload_to=VerificationUpdateImagePath,
    #     blank=True,
    #     verbose_name=_("Screenshot"),
    #     help_text=_("This should be your TOTAL XP screenshot."),
    #     )
    
    # Error Override Checks
    # TODO: Replace this with a front-end check.
    double_check_confirmation = models.BooleanField(
        default=False,
        verbose_name=_("I have double checked this information and it is correct."),
        help_text=_("This will silence some errors."),
        )
    
    # Can be seen on main profile
    total_xp = models.PositiveIntegerField(
        null=True, # Are you sure you want this?
        verbose_name=pgettext_lazy("total_xp__title", "Total XP"),
        )
    
    # Pokedex Figures
    pokedex_total_caught = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_total_caught__title", "Unique Species Caught"),
        )
    pokedex_total_seen = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_total_seen__title", "Unique Species Seen"),
        )
    pokedex_gen1 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen1__title", "Kanto"),
        help_text=pgettext_lazy("pokedex_gen1__help", "Register {0} Kanto region Pokémon in the Pokédex.").format(100),
        validators=[MaxValueValidator(151)],
        )
    pokedex_gen2 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen2__title", "Johto"),
        help_text=pgettext_lazy("pokedex_gen2__help", "Register {0} Pokémon first discovered in the Johto region to the Pokédex.").format(70),
        validators=[MaxValueValidator(100)],
        )
    pokedex_gen3 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen3_title", "Hoenn"),
        help_text=pgettext_lazy("pokedex_gen3", "Register {0} Pokémon first discovered in the Hoenn region to the Pokédex.").format(90),
        validators=[MaxValueValidator(134)],
        )
    pokedex_gen4 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen4__title", "Sinnoh"),
        help_text=pgettext_lazy("pokedex_gen4__help", "Register {0} Pokémon first discovered in the Sinnoh region to the Pokédex.").format(80),
        validators=[MaxValueValidator(107)],
        )
    pokedex_gen5 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen5__title", "Unova"),
        help_text=pgettext_lazy("pokedex_gen5__help", "Register {0} Pokémon first discovered in the Unova region to the Pokédex.").format(100),
        validators=[MaxValueValidator(156)],
        )
    pokedex_gen6 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen6__title", "Kalos"),
        help_text=pgettext_lazy("pokedex_gen6__help", "Register {0} Pokémon first discovered in the Kalos region to the Pokédex.").format('x'),
        validators=[MaxValueValidator(72)],
        )
    pokedex_gen7 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen7__title", "Alola"),
        help_text=pgettext_lazy("pokedex_gen7__help", "Register {0} Pokémon first discovered in the Alola region to the Pokédex.").format('x'),
        validators=[MaxValueValidator(88)],
        )
    pokedex_gen8 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_gen8__title", "Galar"),
        help_text=pgettext_lazy("pokedex_gen8__help", "Register {0} Pokémon first discovered in the Galar region to the Pokédex.").format('x'),
        validators=[MaxValueValidator(87)],
        )
    
    # Medals
    travel_km = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="{title} | {alt}".format(
            title=pgettext_lazy("travel_km__title", "Jogger"),
            alt=pgettext_lazy("travel_km__title_alt", "Distance Walked"),
            ),
        help_text=pgettext_lazy("travel_km__help", "Walk {0:0,g} km").format(1000.0),
        )
    capture_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="{title} | {alt}".format(
            title=pgettext_lazy("capture_total__title", "Collector"),
            alt=pgettext_lazy("capture_total__title_alt", "Pokémon Caught"),
            ),
        help_text=pgettext_lazy("capture_total__help", "Catch {0} Pokémon.").format(2000),
        )
    evolved_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("evolved_total__title", "Scientist"),
        help_text=pgettext_lazy("evolved_total__help", "Evolve {0} Pokémon.").format(200),
        )
    hatched_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("hatched_total__title", "Breeder"),
        help_text=pgettext_lazy("hatched_total__help", "Hatch {0} eggs.").format(500),
        )
    pokestops_visited = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="{title} | {alt}".format(
            title=pgettext_lazy("pokestops_visited__title", "Backpacker"),
            alt=pgettext_lazy("pokestops_visited__title_alt", "PokéStops Visited"),
            ),
        help_text=pgettext_lazy("pokestops_visited__help", "Visit {0} PokéStops.").format(2000),
        )
    big_magikarp = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("big_magikarp__title", "Fisherman"),
        help_text=pgettext_lazy("big_magikarp__help", "Catch {0} big Magikarp.").format(300),
        )
    battle_attack_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_attack_won__title", "Battle Girl"),
        help_text=pgettext_lazy("battle_attack_won__help", "Win {0} Gym battles.").format(1000),
        )
    battle_training_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_training_won__title", "Ace Trainer"),
        help_text=pgettext_lazy("battle_training_won__help", "Train {0} times.").format(1000),
        )
    small_rattata = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("small_rattata__title", "Youngster"),
        help_text=pgettext_lazy("small_rattata__help", "Catch {0} tiny Rattata.").format(300),
        )
    pikachu = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pikachu__title", "Pikachu Fan"),
        help_text=pgettext_lazy("pikachu__help", "Catch {0} Pikachu.").format(300),
        )
    unown = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("unown__title", "Unown"),
        help_text=pgettext_lazy("unown__help", "Catch {0} Unown.").format(26),
        validators=[MaxValueValidator(28)],
        )
    raid_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("raid_battle_won__title", "Champion"),
        help_text=pgettext_lazy("raid_battle_won__help", "Win {0} Raids.").format(1000),
        )
    legendary_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("legendary_battle_won__title", "Battle Legend"),
        help_text=pgettext_lazy("legendary_battle_won__help", "Win {0} Legendary Raids.").format(1000),
        )
    berries_fed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("berries_fed__title", "Berry Master"),
        help_text=pgettext_lazy("berries_fed__help", "Feed {0} Berries at Gyms.").format(1000),
        )
    hours_defended = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("hours_defended__title", "Gym Leader"),
        help_text=pgettext_lazy("hours_defended__help", "Defend Gyms for {0} hours.").format(1000),
        )
    challenge_quests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("challenge_quests__title", "Pokémon Ranger"),
        help_text=pgettext_lazy("challenge_quests__help", "Complete {0} Field Research tasks.").format(1000),
        )
    max_level_friends = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("max_level_friends__title", "Idol"),
        help_text=pgettext_lazy("max_level_friends__help", "Become Best Friends with {0} Trainers.").format(3),
        )
    trading = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("trading__title", "Gentleman"),
        help_text=pgettext_lazy("trading__help", "Trade {0} Pokémon.").format(1000),
        )
    trading_distance = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("trading_distance__title", "Pilot"),
        help_text=pgettext_lazy("trading_distance__help", "Earn {0} km across the distance of all Pokémon trades.").format(1000000),
        )
    great_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("great_league__title", "Great League Veteran"),
        help_text=pgettext_lazy("great_league__help", "Win {} Trainer Battles in the Great League.").format(200),
        )
    ultra_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("ultra_league__title", "Ultra League Veteran"),
        help_text=pgettext_lazy("ultra_league__help", "Win {} Trainer Battles in the Ultra League.").format(200),
        )
    master_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("master_league__title", "Master League Veteran"),
        help_text=pgettext_lazy("master_league__help", "Win {} Trainer Battles in the Master League.").format(200),
        )
    photobomb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("photobomb__title", "Cameraman"),
        help_text=pgettext_lazy("photobomb__help", "Have {0} surprise encounters in AR Snapshot.").format(200),
        )
    pokemon_purified = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokemon_purified__title", "Purifier"),
        help_text=pgettext_lazy("pokemon_purified__help", "Purify {0} Shadow Pokémon.").format(500),
        )
    rocket_grunts_defeated = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("rocket_grunts_defeated__title", "Hero"),
        help_text=pgettext_lazy("rocket_grunts_defeated__help", "Defeat {0} Team GO Rocket Grunts.").format(1000),
        )
    wayfarer = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("wayfarer__title", "Wayfarer"),
        help_text=pgettext_lazy("wayfarer__help", "Earn {0} Wayfarer Agreements").format(1000),
        )
    
    type_normal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_normal__title", "Schoolkid"),
        help_text=pgettext_lazy("type_normal__help", "Catch {0} Normal-type Pokémon").format(200),
        )
    type_fighting = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fighting__title", "Black Belt"),
        help_text=pgettext_lazy("type_fighting__help", "Catch {0} Fighting-type Pokémon").format(200),
        )
    type_flying = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_flying__title", "Bird Keeper"),
        help_text=pgettext_lazy("type_flying__help", "Catch {0} Flying-type Pokémon").format(200),
        )
    type_poison = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_poison__title", "Punk Girl"),
        help_text=pgettext_lazy("type_poison__help", "Catch {0} Poison-type Pokémon").format(200),
        )
    type_ground = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ground__title", "Ruin Maniac"),
        help_text=pgettext_lazy("type_ground__help", "Catch {0} Ground-type Pokémon").format(200),
        )
    type_rock = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_rock__title", "Hiker"),
        help_text=pgettext_lazy("type_rock__help", "Catch {0} Rock-type Pokémon").format(200),
        )
    type_bug = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_bug__title", "Bug Catcher"),
        help_text=pgettext_lazy("type_bug__help", "Catch {0} Bug-type Pokémon").format(200),
        )
    type_ghost = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ghost__title", "Hex Maniac"),
        help_text=pgettext_lazy("type_ghost__help", "Catch {0} Ghost-type Pokémon").format(200),
        )
    type_steel = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_steel__title", "Depot Agent"),
        help_text=pgettext_lazy("type_steel__help", "Catch {0} Steel-type Pokémon").format(200),
        )
    type_fire = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fire__title", "Kindler"),
        help_text=pgettext_lazy("type_fire__help", "Catch {0} Fire-type Pokémon").format(200),
        )
    type_water = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_water__title", "Swimmer"),
        help_text=pgettext_lazy("type_water__help", "Catch {0} Water-type Pokémon").format(200),
        )
    type_grass = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_grass__title", "Gardener"),
        help_text=pgettext_lazy("type_grass__help", "Catch {0} Grass-type Pokémon").format(200),
        )
    type_electric = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_electric__title", "Rocker"),
        help_text=pgettext_lazy("type_electric__help", "Catch {0} Electric-type Pokémon").format(200),
        )
    type_psychic = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_psychic__title", "Psychic"),
        help_text=pgettext_lazy("type_psychic__help", "Catch {0} Pychic-type Pokémon").format(200),
        )
    type_ice = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ice__title", "Skier"),
        help_text=pgettext_lazy("type_ice__help", "Catch {0} Ice-type Pokémon").format(200),
        )
    type_dragon = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_dragon__title", "Dragon Tamer"),
        help_text=pgettext_lazy("type_dragon__help", "Catch {0} Dragon-type Pokémon").format(200),
        )
    type_dark = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_dark__title", "Delinquent"),
        help_text=pgettext_lazy("type_dark__help", "Catch {0} Dark-type Pokémon").format(200),
        )
    type_fairy = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fairy__title", "Fairy Tale Girl"),
        help_text=pgettext_lazy("type_fairy__help", "Catch {0} Fairy-type Pokémon").format(200),
        )
    
    # Extra Questions
    gymbadges_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("gymbadges_total__title", "Gym Badges"),
        validators=[MaxValueValidator(1000)],
        )
    gymbadges_gold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("gymbadges_gold__title", "Gold Gym Badges"),
        )
    stardust = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("stardust__title", "Stardust"),
        )
    
    def __str__(self):
        return "Update(trainer: {trainer}, update_time: {time}, {stats})".format(
            trainer=self.trainer,
            time=self.update_time,
            stats=','.join([f'{x}: {getattr(self, x)}' for x in self.modified_fields()]),
            )
    
    def has_modified_extra_fields(self) -> bool:
        return bool(list(self.modified_extra_fields()))
    has_modified_extra_fields.boolean = True

    def modified_fields(self):
        fields = []
        fields += UPDATE_FIELDS_BADGES
        fields += UPDATE_FIELDS_TYPES
        fields += UPDATE_FIELDS_POKEDEX
        fields += 'gymbadges_total'
        fields += 'gymbadges_gold'
        fields += 'stardust'
        fields += 'total_xp'
        
        for x in fields:
            if getattr(self, x):
                yield x
    
    def modified_extra_fields(self):
        fields = []
        fields += UPDATE_FIELDS_BADGES
        fields += UPDATE_FIELDS_TYPES
        fields += UPDATE_FIELDS_POKEDEX
        fields += 'gymbadges_total'
        fields += 'gymbadges_gold'
        fields += 'stardust'
        
        for x in fields:
            if getattr(self, x):
                yield x
    
    def clean(self):
        errors = defaultdict(list)
            
        for field in Update._meta.get_fields():
            if getattr(self, field.name) is None:
                continue # Nothing to check!
            
            
            # Get latest update with that field present, only get the important fields.
            last_update = self.trainer.update_set.filter(update_time__lt=self.update_time) \
                .exclude(uuid=self.uuid) \
                .exclude(**{field.name : None}) \
                .order_by('-update_time') \
                .only(field.name, 'update_time') \
                .first()
            
            # Overall Rules
            
            # Value must be higher than or equal to than previous value
            if last_update is not None and field.name in UPDATE_NON_REVERSEABLE_FIELDS:
                if getattr(self, field.name) < getattr(last_update, field.name):
                    errors[field.name].append(
                        ValidationError(
                            _("This value has previously been entered at a higher value. Please try again ensuring the value you entered was correct."),
                            code='insufficient',
                            ),
                        )
            
            # Field specific Validation
            
            if field.name == 'gymbadges_gold':
                
                # Max Value = 1000, unless total is at 1000
                
                max_gymbadges_visible = 1000
                gold = getattr(self,field.name)
                total = getattr(self,'gymbadges_total')
                
                
                # Check if gymbadges_total is filled in
                if total is None:
                    errors['gymbadges_total'].append(
                        ValidationError(
                            _("This is required since you provided data for {badge}.").format(badge=field.verbose_name),
                            code='required',
                            ),
                        )
                elif total < max_gymbadges_visible and gold > total:
                    errors[field.name].append(
                        ValidationError(
                            _("Stat too high. Must be less than {badge}.").format(badge=Update._meta.get_field('gymbadges_total').verbose_name),
                            code='excessive',
                            ),
                        )
            
            if field.name == 'trading_distance':
                
                trading = getattr(self,'trading')
                
                # Check if trading is filled in
                if trading is None:
                    errors['trading'].append(
                        ValidationError(
                            _("This is required since you provided data for {badge}.").format(badge=field.verbose_name),
                            code='required',
                            ),
                        )
                
        if errors:
            raise ValidationError(errors)
    
    def check_values(self, raise_: bool=False):
        """Checks values for anything ary
        
        Parameters
        ----------
        raise_: bool
            If True, will raise an error instead of returning the list of warnings. Useful for returning to forms.
            
        Exceptions
        ----------
        ValidationError: raised is raise_ is True
        
        Returns
        -------
        List of exceptions of raise_ False
        else None
        """
        
        warnings = defaultdict(list)
        
        if self.trainer.start_date:
            start_date = self.trainer.start_date
        else:
            start_date = datetime.date(2016, 7, 5)
        
        config = {
            'total_xp': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 10000000,
                },
            'travel_km': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': Decimal('60.0'),
                },
            'capture_total': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 800,
                },
            'evolved_total': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 250,
                },
            'evolved_total': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 250,
                },
            'evolved_total': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 250,
                },
            'hatched_total': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 60,
                },
            'pokestops_visited': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 500,
                },
            'big_magikarp': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 25,
                },
            'battle_attack_won': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 500,
                },
            'battle_training_won': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date, datetime.date(2018,12,13)),
                    datetime.time.min,
                    ),
                'DailyLimit': 100,
                },
            'small_rattata': {
                'InterestDate': datetime.datetime.combine(
                    start_date,
                    datetime.time.min,
                    ),
                'DailyLimit': 25,
                },
            'berries_fed': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2017,6,22)),
                    datetime.time.min,
                    ),
                'DailyLimit': 100,
                },
            'hours_defended': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2017,6,22)),
                    datetime.time.min,
                    ),
                'DailyLimit': 480,
                },
            'raid_battle_won': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2017,6,26)),
                    datetime.time.min,
                    ),
                'DailyLimit': 100,
                },
            'legendary_battle_won': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2017,7,22)),
                    datetime.time.min,
                    ),
                'DailyLimit': 100,
                },
            'challenge_quests': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2018,3,30)),
                    datetime.time.min,
                    ),
                'DailyLimit': 500,
                },
            'trading': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2018,6,21)),
                    datetime.time.min,
                    ),
                'DailyLimit': 100,
                },
            'trading_distance': {
                'InterestDate': datetime.datetime.combine(
                    max(start_date,datetime.date(2018,6,21)),
                    datetime.time.min,
                    ),
                'DailyLimit': 1001800, # (earth_circumference/2) * trading.DailyLimit
                },
            
        }
        
        
        for field in Update._meta.get_fields():
            if getattr(self, field.name) is None:
                continue # Nothing to check!
            
            # Get latest update with that field present, only get the important fields.
            last_update = self.trainer.update_set.filter(update_time__lt=self.update_time) \
                .exclude(uuid=self.uuid) \
                .exclude(**{field.name : None}) \
                .order_by('-update_time') \
                .only(field.name, 'update_time') \
                .first()
            
            if config.get(field.name):
                if config.get(field.name).get('InterestDate') and config.get(field.name).get('DailyLimit'):
                    rate_limits = [
                        {
                            'stat': 0,
                            'datetime': config.get(field.name).get('InterestDate'),
                        },
                    ]
                    if last_update:
                        rate_limits.append({
                            'stat': getattr(last_update, field.name),
                            'datetime': getattr(last_update, 'update_time'),
                        })
                    
                    for x in rate_limits:
                        stat_delta = getattr(self, field.name)-x['stat']
                        delta = getattr(self, 'update_time')-x['datetime']
                        rate = stat_delta / (delta.total_seconds()/86400)
                        if rate >= config.get(field.name).get('DailyLimit'):
                            warnings[field.name].append(
                                ValidationError(
                                    _("This value is high. Your daily average is above the threshold of {threshold:,}. Please check you haven't made a mistake.\n\nYour daily average between {earlier_date} and {later_date} is {average:,}").format(
                                        threshold=DailyLimit,
                                        average=rate,
                                        earlier_date=x['datetime'],
                                        later_date=getattr(self, 'update_time'),
                                    ),
                                    code='excessive',
                                ),
                            )
            
            if field.name == 'gymbadges_gold':
                
                _xcompare = getattr(self, 'gymbadges_total')
                # Check if gymbadges_total is filled in
                if _xcompare:
                    # GoldGyms < GymsSeen
                    # Check if gymbadges_gold is more of less than gymbadges_total
                    if getattr(self,field.name) > _xcompare:
                        warnings[field.name].append(ValidationError(_("The {badge} you entered is too high. Please check for typos and other mistakes. You can't have more gold gyms than gyms in Total. {value:,}/{expected:,}").format(badge=field.verbose_name, value=getattr(self,field.name), expected=_xcompare)))
                else:
                    warnings[field.name].append(ValidationError(_("You must fill in {other_badge} if filling in {this_badge}.").format(this_badge=field.verbose_name, other_badge=Update._meta.get_field('gymbadges_total').verbose_name)))
                
            if field.name == 'trading_distance':
                
                trading = getattr(self, 'trading')
                earth_circumference = 20037.5085
                max_distance = int(earth_circumference/2)
                rate = (getattr(self,field.name) / _xcompare)
                
                # Check if trading is filled in
                if trading:
                    # Pilot / Gentleman < Half Earth
                    if rate >= max_distance:
                        warnings[field.name].append(
                            ValidationError(
                                _("This value is high. Your distance per trade average is above the threshold of {threshold:,}/trade. Please check you haven't made a mistake.\n\nYour average is {average:,}/trade").format(
                                    threshold=max_distance,
                                    average=rate,
                                ),
                                code='excessive',
                            ),
                        )
                else:
                    warnings[field.name].append(ValidationError(_("You must fill in {other_badge} if filling in {this_badge}.").format(this_badge=field.verbose_name, other_badge=Update._meta.get_field('trading').verbose_name)))
        
        if raise_ and warnings:
                ValidationError(warnings)
        elif raise_ == False:
                return warnings
    
    class Meta:
        get_latest_by = 'update_time'
        ordering = ['-update_time']
        verbose_name = _("Update")
        verbose_name_plural = _("Updates")

# @receiver(post_save, sender=Update)
# def update_discord_level(sender, **kwargs):
#     if kwargs['created'] and kwargs['instance'].total_xp:
#         level = kwargs['instance'].level()
#         for discord in DiscordGuildMembership.objects.exclude(active=False).filter(guild__discordguildsettings__renamer=True, guild__discordguildsettings__renamer_with_level=True, user__user__trainer=kwargs['instance'].trainer):
#             if discord.nick_override:
#                 base = discord.nick_override
#             else:
#                 base = kwargs['instance'].trainer.nickname
#
#             if discord.guild.discordguildsettings.renamer_with_level_format=='int':
#                 ext = str(level)
#             elif discord.guild.discordguildsettings.renamer_with_level_format=='circled_level':
#                 ext = circled_level(level)
#
#             if len(base)+len(ext) > 32:
#                 chopped_base = base[slice(0,32-len(ext)-1)]
#                 combined = f"{chopped_base}…{ext}"
#             elif len(base)+len(ext) == 32:
#                 combined = f"{base}{ext}"
#             else:
#                 combined = f"{base} {ext}"
#
#             discord._change_nick(combined)
