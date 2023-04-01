from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from os.path import splitext
from typing import TYPE_CHECKING, Literal, NoReturn
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import npgettext_lazy, pgettext_lazy
from django_countries.fields import CountryField
from exclusivebooleanfield.fields import ExclusiveBooleanField

from config.abstract_models import PublicModel
from core.models.discord import DiscordGuild, DiscordGuildMembership, DiscordRole
from pokemongo.fields import (
    BaseStatistic,
    BigIntegerStatistic,
    DecimalStatistic,
    IntegerStatistic,
)
from pokemongo.shortcuts import circled_level, get_possible_levels_from_total_xp
from pokemongo.validators import PokemonGoUsernameValidator, TrainerCodeValidator

logger = logging.getLogger("django.trainerdex")

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def get_path_for_badges(instance: ProfileBadge, filename: str) -> str:
    return f"profile/badges/{instance.slug}{splitext(filename)[1]}"


class Faction:
    def __init__(self, id: int):
        if not (0 <= id <= 3):
            raise ValueError("Must be one of four choices: 0, 1, 2, 3")
        self.id: int = id
        self.verbose_name: str = settings.TEAMS[self.id]

    def get_image_url(self) -> str:
        return static(f"img/faction/{self.id}.png")

    def __str__(self) -> str:
        return str(self.verbose_name)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, Faction):
            return self.id == other.id
        else:
            raise NotImplementedError

    def __bool__(self) -> bool:
        return True


class Trainer(PublicModel):
    owner: User = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer",
        verbose_name=_("User"),
    )

    _nickname: str = postgres_fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        db_index=True,
        verbose_name=pgettext_lazy("codename", "Nickname"),
        help_text="A local cached version of a trainers nickname.",
        editable=False,
    )

    start_date: date | None = models.DateField(
        null=True,
        blank=True,
        validators=[MinValueValidator(date(2016, 7, 5))],
        verbose_name=pgettext_lazy("profile_start_date", "Start Date"),
        help_text=_("The date you created your Pokémon Go account."),
    )
    faction: Literal[0, 1, 2, 3] | None = models.SmallIntegerField(
        choices=list(settings.TEAMS.items()),
        null=True,
        verbose_name=pgettext_lazy("faction", "Team"),
    )
    last_cheated: date | None = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Cheated"),
        help_text=_("When did this Trainer last cheat?"),
    )
    statistics: bool = models.BooleanField(
        default=True,
        verbose_name=pgettext_lazy("profile_category_stats", "Stats"),
        help_text=_(
            "Would you like to be shown on the leaderboard?"
            " Ticking this box gives us permission to process your data."
        ),
    )

    daily_goal: int | None = models.PositiveIntegerField(null=True, blank=True)
    total_goal: int | None = models.BigIntegerField(
        null=True, blank=True, validators=[MinValueValidator(100)]
    )

    trainer_code: str | None = models.CharField(
        null=True,
        blank=True,
        validators=[TrainerCodeValidator],
        max_length=15,
        verbose_name=pgettext_lazy("friend_code_title", "Trainer Code"),
        help_text=_("Fancy sharing your trainer code?" " (This information is public.)"),
    )

    country = CountryField(
        null=True,
        blank=True,
        multiple=False,
        verbose_name=_("Country"),
        help_text=_("Where are you based?"),
    )

    verified: bool = models.BooleanField(default=False, verbose_name=_("Verified"))

    @property
    def last_modified(self) -> datetime:
        return self.updated_at

    event_10b: bool = models.BooleanField(default=False)
    event_1k_users: bool = models.BooleanField(default=False)

    legacy_40: bool = models.BooleanField(
        default=False,
        verbose_name=pgettext_lazy("level_40_title", "Legacy 40"),
        help_text=pgettext_lazy("level_40", "Achieve level 40 by December 31, 2020."),
    )

    def team(self) -> Faction | None:
        if self.faction:
            return Faction(int(self.faction))

    def has_cheated(self) -> bool:
        return bool(self.last_cheated)

    has_cheated.boolean = True
    has_cheated.short_description = _("Has Cheated")

    def currently_banned(self, d: date | None = None) -> bool:
        # Bans are supposed to last 6 months, the change was made on 2018-09-01. However, my code
        # has been bugged and since I never checked in on cheaters, since they mostly left I never
        # spotted the bug. Given the SARS-COVID-19 outbreak, I've decided to reduce punishment time
        # within that time period to TWELVE weeks. I have also decided to extend the 6 month period
        # to before 2018-09-01, since it's a little unfair.

        cheat_date = self.last_cheated
        if not cheat_date:
            return False
        current_date = d or timezone.now().date()
        COVID_START: date = date(2019, 12, 31)
        COVID_END: date = date(2021, 12, 31)  # 2 years in generous, adjust to suit

        if COVID_START < cheat_date < COVID_END:
            # During the SARS-COVID-19 outbreak, ban length is 12 weeks.
            return cheat_date + timedelta(weeks=12) > current_date
        else:
            # Else the ban length is 26 weeks.
            return cheat_date + timedelta(weeks=26) > current_date

    currently_banned.boolean = True
    currently_banned.short_description = _("Banned")
    currently_cheats = currently_banned

    def is_prefered(self) -> Literal[True]:
        return True

    def verification_status(self) -> str:
        return _("Verified") if self.verified else _("Unverified")

    verification_status.short_description = _("Verification Status")

    def is_on_leaderboard(self) -> bool:
        return self.verified and self.statistics and not self.currently_banned()

    is_on_leaderboard.boolean = True

    def get_level(self) -> str | int | None:
        if (level := getattr(self, "level", None)) is not None:
            return level

        try:
            update: Update = self.update_set.only("trainer_level").latest("update_time")
        except Update.DoesNotExist:
            return None
        else:
            return update.trainer_level

    @property
    def active(self) -> bool:
        return self.owner.is_active

    @property
    def profile_complete(self) -> bool:
        return self.verified

    profile_completed_optional = profile_complete

    @property
    def nickname(self) -> str:
        """Gets nickname, fallback to User username"""
        return self._nickname

    @property
    def username(self) -> str:
        """Alias for nickname"""
        return self.nickname

    @property
    def user(self) -> str:
        """Alias for owner"""
        return self.owner

    def __str__(self) -> str:
        return self.nickname

    def get_absolute_url(self) -> str:
        return reverse("trainerdex:profile", kwargs={"nickname": self.nickname})

    def soft_delete(self, *args, cascade: bool = True, **kwargs) -> Counter[dict[str, int]]:
        if self.is_deleted:
            return Counter()

        deletetion_time = kwargs.pop("updated_at", timezone.now())
        if cascade:
            with transaction.atomic():
                if self.owner.is_active:
                    self.owner.is_active = False
                    self.owner.save(update_fields={"is_active"})
                    owner_counter = Counter({str(self.owner._meta): 1})
                else:
                    owner_counter = Counter()

                updates_counter = Counter()
                for update in self.update_set.filter(is_deleted=False):
                    updates_counter += update.soft_delete(updated_at=deletetion_time)

                self_counter = super().soft_delete(*args, updated_at=deletetion_time, **kwargs)
            return owner_counter + updates_counter + self_counter

        return super().soft_delete(*args, updated_at=deletetion_time, **kwargs)

    def undelete(self, *args, cascade: bool = True, **kwargs) -> Counter[dict[str, int]]:
        if not self.is_deleted:
            return Counter()

        restore_time = kwargs.pop("updated_at", timezone.now())
        if cascade:
            with transaction.atomic():
                if self.owner.is_active is False:
                    self.owner.is_active = True
                    self.owner.save(update_fields={"is_active"})
                    owner_counter = Counter({str(self.owner._meta): 1})
                else:
                    owner_counter = Counter()

                updates_counter = Counter()
                for update in self.update_set.filter(
                    is_deleted=True,
                    deleted_at__gte=self.deleted_at,
                ):
                    updates_counter += update.undelete(updated_at=restore_time)

                self_counter = super().undelete(*args, updated_at=restore_time, **kwargs)
            return owner_counter + updates_counter + self_counter

        return super().undelete(*args, updated_at=restore_time, **kwargs)

    if TYPE_CHECKING:
        nickname_set: models.QuerySet[Nickname]
        update_set: models.QuerySet[Update]

    class Meta:
        verbose_name = _("Trainer")
        verbose_name_plural = _("Trainers")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(
    sender: type[models.Model],
    created: bool = None,
    raw: bool = None,
    instance: User = None,
    **kwargs,
) -> Trainer | None:
    if created and not raw:
        trainer = Trainer.objects.create(_nickname=instance.username, owner=instance)
        return trainer


class Nickname(models.Model):
    trainer: Trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=pgettext_lazy("player_term", "Trainer"),
    )
    nickname: str = postgres_fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        db_index=True,
        verbose_name=pgettext_lazy("codename", "Nickname"),
    )
    active: bool = ExclusiveBooleanField(on="trainer")

    def clean(self) -> None:
        if self.active and (
            (self.trainer.owner.username != self.nickname)
            or (self.trainer._nickname != self.nickname)
        ):
            if self.trainer.owner.username != self.nickname:
                self.trainer.owner.username = self.nickname
                self.trainer.owner.save(update_fields=["username"])
            if self.trainer._nickname != self.nickname:
                self.trainer._nickname = self.nickname
                self.trainer.save(update_fields=["_nickname"])

    def __str__(self) -> str:
        return self.nickname

    class Meta:
        ordering = ["nickname"]


@receiver(post_save, sender=Trainer)
def new_trainer_set_nickname(
    sender: type[models.Model],
    created: bool = None,
    raw: bool = None,
    instance: Trainer = None,
    **kwargs,
) -> Nickname | None:
    if created and not raw:
        nickname = Nickname.objects.create(
            trainer=instance,
            nickname=instance.owner.username,
            active=True,
        )
        return nickname


class Update(PublicModel):
    trainer: Trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        verbose_name=_("Trainer"),
    )
    update_time: datetime = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Time Updated"),
    )

    DATABASE_SOURCES = (
        ("?", None),
        ("cs_social_twitter", "Twitter (Found)"),
        ("cs_social_facebook", "Facebook (Found)"),
        ("cs_social_youtube", "YouTube (Found)"),
        ("cs_?", "Sourced Elsewhere"),
        ("ts_social_discord", "Discord"),
        ("ts_social_twitter", "Twitter"),
        ("ts_direct", "Directly told (via text)"),
        ("web_quick", "Quick Update (Web)"),
        ("web_detailed", "Detailed Update (Web)"),
        ("ts_registration", "Registration"),
        ("ss_registration", "Registration w/ Screenshot"),
        ("ss_generic", "Generic Screenshot"),
        ("ss_ocr", "OCR Screenshot"),
        ("com.nianticlabs.pokemongo.friends", "In Game Friends"),
        ("com.pokeassistant.trainerstats", "Poké Assistant"),
        ("com.pokenavbot.profiles", "PokeNav"),
        ("tl40datateam.spreadsheet", "Tl40 Data Team (Legacy)"),
        ("com.tl40data.website", "Tl40 Data Team"),
        ("com.pkmngots.import", "Third Saturday"),
    )

    data_source: str = models.CharField(
        max_length=256,
        choices=DATABASE_SOURCES,
        default="?",
        verbose_name=_("Source"),
    )

    # Can be seen on main profile
    total_xp: int | None = BigIntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("profile_total_xp", "Total XP"),
        validators=[MinValueValidator(100)],
    )
    trainer_level: int | None = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("profile_trainer_level", "Trainer Level"),
        validators=[MinValueValidator(1), MaxValueValidator(50)],
    )

    # Pokedex Figures
    pokedex_caught: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_page_caught", "Unique Species Caught"),
        help_text=pgettext_lazy(
            "pokedex_help",
            "You can find this by clicking the {screen_title_pokedex} button in your game. It should then be listed at the top of the screen.",
        ).format(screen_title_pokedex=pgettext_lazy("screen_title_pokedex", "POKÉDEX")),
        validators=[MinValueValidator(1)],
    )
    pokedex_seen: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_page_seen", "Unique Species Seen"),
        help_text=pgettext_lazy(
            "pokedex_help",
            "You can find this by clicking the {screen_title_pokedex} button in your game. It should then be listed at the top of the screen.",
        ).format(screen_title_pokedex=pgettext_lazy("screen_title_pokedex", "POKÉDEX")),
        validators=[MinValueValidator(1)],
    )

    # Medals
    # 1
    travel_km: Decimal | None = DecimalStatistic(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("travel_km_title", "Jogger"),
        help_text=pgettext_lazy("travel_km_help", "Walk {0:0,g} km.").format(10000.0),
        validators=[MinValueValidator(Decimal(0.0))],
        stat_id=1,
        bronze=Decimal(10),
        silver=Decimal(100),
        gold=Decimal(1000),
        platinum=Decimal(10000),
    )
    # 2
    pokedex_entries: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_title", "Kanto"),
        help_text=pgettext_lazy(
            "pokedex_entries_help", "Register {0} Kanto region Pokémon in the Pokédex."
        ).format(151),
        validators=[MaxValueValidator(151), MinValueValidator(1)],
        stat_id=2,
        bronze=5,
        silver=50,
        gold=100,
        platinum=151,
    )
    # 3
    capture_total: int | None = BigIntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("capture_total_title", "Collector"),
        help_text=pgettext_lazy("capture_total_help", "Catch {0} Pokémon.").format(50000),
        validators=[MinValueValidator(1)],
        stat_id=3,
        bronze=30,
        silver=500,
        gold=2000,
        platinum=50000,
    )
    # 5
    evolved_total: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("evolved_total_title", "Scientist"),
        help_text=pgettext_lazy("evolved_total_help", "Evolve {0} Pokémon.").format(2000),
        stat_id=5,
        bronze=3,
        silver=20,
        gold=200,
        platinum=2000,
    )
    # 6
    hatched_total: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("hatched_total_title", "Breeder"),
        help_text=pgettext_lazy("hatched_total_help", "Hatch {0} eggs.").format(2500),
        stat_id=6,
        bronze=10,
        silver=100,
        gold=500,
        platinum=2500,
    )
    # 8
    pokestops_visited: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokestops_visited_title", "Backpacker"),
        help_text=pgettext_lazy("pokestops_visited_help", "Visit {0} PokéStops.").format(50000),
        stat_id=8,
        bronze=100,
        silver=1000,
        gold=2000,
        platinum=50000,
    )
    # 9
    unique_pokestops: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("unique_pokestops_title", "Sightseer"),
        help_text=npgettext_lazy(
            "unique_pokestops_help",
            "Visit a PokéStop.",
            "Visit {0} unique PokéStops.",
            2000,
        ).format(2000),
        stat_id=9,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 11
    big_magikarp: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("big_magikarp_title", "Fisher"),
        help_text=pgettext_lazy("big_magikarp_help", "Catch {0} big Magikarp.").format(1000),
        stat_id=11,
        bronze=3,
        silver=50,
        gold=300,
        platinum=1000,
    )
    # 13
    battle_attack_won: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_attack_won_title", "Battle Girl"),
        help_text=pgettext_lazy("battle_attack_won_help", "Win {0} Gym battles.").format(4000),
        stat_id=13,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=4000,
    )
    # 14
    battle_training_won: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_training_won_title", "Ace Trainer"),
        help_text=pgettext_lazy("battle_training_won_help", "Train {0} times.").format(2000),
        stat_id=14,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 36
    small_rattata: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("small_rattata_title", "Youngster"),
        help_text=pgettext_lazy("small_rattata_help", "Catch {0} tiny Rattata.").format(1000),
        stat_id=36,
        bronze=3,
        silver=50,
        gold=300,
        platinum=1000,
    )
    # 37
    pikachu: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pikachu_title", "Pikachu Fan"),
        help_text=pgettext_lazy("pikachu_help", "Catch {0} Pikachu.").format(1000),
        stat_id=37,
        bronze=3,
        silver=50,
        gold=300,
        platinum=1000,
    )
    # 38
    unown: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("unown_title", "Unown"),
        help_text=pgettext_lazy("unown_help", "Catch {0} Unown.").format(28),
        validators=[
            MaxValueValidator(28),
        ],
        stat_id=38,
        bronze=3,
        silver=10,
        gold=26,
        platinum=28,
    )
    # 39
    pokedex_entries_gen2: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen2_title", "Johto"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen2_help",
            "Register {0} Pokémon first discovered in the Johto region to the Pokédex.",
        ).format(100),
        validators=[
            MaxValueValidator(100),
        ],
        stat_id=39,
        bronze=3,
        silver=10,
        gold=26,
        platinum=100,
    )
    # 40
    raid_battle_won: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("raid_battle_won_title", "Champion"),
        help_text=pgettext_lazy("raid_battle_won_help", "Win {0} raids.").format(2000),
        stat_id=40,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 41
    legendary_battle_won: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("legendary_battle_won_title", "Battle Legend"),
        help_text=pgettext_lazy("legendary_battle_won_help", "Win {0} Legendary raids.").format(
            2000
        ),
        stat_id=41,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 42
    berries_fed: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("berries_fed_title", "Berry Master"),
        help_text=pgettext_lazy("berries_fed_help", "Feed {0} Berries at Gyms.").format(15000),
        stat_id=42,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=15000,
    )
    # 43
    hours_defended: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("hours_defended_title", "Gym Leader"),
        help_text=pgettext_lazy("hours_defended_help", "Defend Gyms for {0} hours.").format(15000),
        stat_id=43,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=15000,
    )
    # 45
    pokedex_entries_gen3: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen3_title", "Hoenn"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen3_help",
            "Register {0} Pokémon first discovered in the Hoenn region to the Pokédex.",
        ).format(135),
        validators=[
            MaxValueValidator(135),
        ],
        stat_id=45,
        bronze=5,
        silver=40,
        gold=90,
        platinum=135,
    )
    # 46
    challenge_quests: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("challenge_quests_title", "Pokémon Ranger"),
        help_text=pgettext_lazy(
            "challenge_quests_help", "Complete {0} Field Research tasks."
        ).format(2500),
        stat_id=46,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2500,
    )
    # 48
    max_level_friends: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("max_level_friends_title", "Idol"),
        help_text=npgettext_lazy(
            context="max_level_friends_help",
            singular="Become Best Friends with {0} Trainer.",
            plural="Become Best Friends with {0} Trainers.",
            number=20,
        ).format(20),
        stat_id=48,
        bronze=1,
        silver=2,
        gold=3,
        platinum=20,
    )
    # 49
    trading: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("trading_title", "Gentleman"),
        help_text=pgettext_lazy("trading_help", "Trade {0} Pokémon.").format(2500),
        stat_id=49,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2500,
    )
    # 50
    trading_distance: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("trading_distance_title", "Pilot"),
        help_text=pgettext_lazy(
            "trading_distance_help",
            "Earn {0} km across the distance of all Pokémon trades.",
        ).format(10000000),
        stat_id=50,
        bronze=1000,
        silver=10000,
        gold=1000000,
        platinum=10000000,
    )
    # 51
    pokedex_entries_gen4: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen4__title", "Sinnoh"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen4_help",
            "Register {0} Pokémon first discovered in the Sinnoh region to the Pokédex.",
        ).format(107),
        validators=[
            MaxValueValidator(107),
        ],
        stat_id=51,
        bronze=5,
        silver=30,
        gold=80,
        platinum=107,
    )
    # 52
    great_league: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("great_league_title", "Great League Veteran"),
        help_text=npgettext_lazy(
            context="great_league_help",
            singular="Win a Trainer Battle in the Great League.",
            plural="Win {0} Trainer Battles in the Great League.",
            number=1000,
        ).format(1000),
        stat_id=52,
        bronze=5,
        silver=50,
        gold=200,
        platinum=1000,
    )
    # 53
    ultra_league: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("ultra_league_title", "Ultra League Veteran"),
        help_text=npgettext_lazy(
            context="ultra_league_help",
            singular="Win a Trainer Battle in the Ultra League.",
            plural="Win {0} Trainer Battles in the Ultra League.",
            number=1000,
        ).format(1000),
        stat_id=53,
        bronze=5,
        silver=50,
        gold=200,
        platinum=1000,
    )
    # 54
    master_league: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("master_league_title", "Master League Veteran"),
        help_text=npgettext_lazy(
            context="master_league_help",
            singular="Win a Trainer Battle in the Master League.",
            plural="Win {0} Trainer Battles in the Master League.",
            number=1000,
        ).format(1000),
        stat_id=54,
        bronze=5,
        silver=50,
        gold=200,
        platinum=1000,
    )
    # 55
    photobomb: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("photobomb_title", "Cameraman"),
        help_text=npgettext_lazy(
            context="photobomb_help",
            singular="Have {0} surprise encounter in GO Snapshot.",
            plural="Have {0} surprise encounters in GO Snapshot.",
            number=400,
        ).format(400),
        stat_id=55,
        bronze=10,
        silver=50,
        gold=200,
        platinum=400,
    )
    # 56
    pokedex_entries_gen5: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen5__title", "Unova"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen5_help",
            "Register {0} Pokémon first discovered in the Unova region to the Pokédex.",
        ).format(156),
        validators=[
            MaxValueValidator(156),
        ],
        stat_id=56,
        bronze=5,
        silver=50,
        gold=100,
        platinum=156,
    )
    # 57
    pokemon_purified: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokemon_purified_title", "Purifier"),
        help_text=pgettext_lazy("pokemon_purified_help", "Purify {0} Shadow Pokémon.").format(
            1000
        ),
        stat_id=57,
        bronze=5,
        silver=50,
        gold=500,
        platinum=1000,
    )
    # 58
    rocket_grunts_defeated: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("rocket_grunts_defeated_title", "Hero"),
        help_text=pgettext_lazy(
            "rocket_grunts_defeated_help", "Defeat {0} Team GO Rocket Grunts."
        ).format(2000),
        stat_id=58,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 59
    rocket_giovanni_defeated: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("rocket_giovanni_defeated_title", "Ultra Hero"),
        help_text=npgettext_lazy(
            context="rocket_giovanni_defeated_help",
            singular="Defeat the Team GO Rocket Boss.",
            plural="Defeat the Team GO Rocket Boss {0} times. ",
            number=50,
        ).format(50),
        stat_id=59,
        bronze=1,
        silver=5,
        gold=20,
        platinum=50,
    )
    # 60
    buddy_best: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("buddy_best_title", "Best Buddy"),
        help_text=npgettext_lazy(
            context="buddy_best_help",
            singular="Have 1 Best Buddy.",
            plural="Have {0} Best Buddies.",
            number=200,
        ).format(200),
        stat_id=60,
        bronze=1,
        silver=10,
        gold=100,
        platinum=2000,
    )
    # 61
    pokedex_entries_gen6: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen6__title", "Kalos"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen6_help",
            "Register {0} Pokémon first discovered in the Kalos region to the Pokédex.",
        ).format(72),
        validators=[
            MaxValueValidator(72),
        ],
        stat_id=61,
        bronze=5,
        silver=25,
        gold=50,
        platinum=72,
    )
    # 62
    pokedex_entries_gen7: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen7__title", "Alola"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen7_help",
            "Register {0} Pokémon first discovered in the Alola region to the Pokédex.",
        ).format(50),
        validators=[
            MaxValueValidator(88),
        ],
        stat_id=62,
        bronze=5,
        silver=25,
        gold=50,
        platinum=86,
    )
    # 63
    pokedex_entries_gen8: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen8__title", "Galar"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen8_help",
            "Register {0} Pokémon first discovered in the Alola region to the Pokédex.",
        ).format(50),
        validators=[
            MaxValueValidator(89),
        ],
        stat_id=63,
        bronze=5,
        silver=25,
        gold=50,
        platinum=89,
    )
    # 64
    seven_day_streaks: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("seven_day_streaks_title", "Triathlete"),
        help_text=npgettext_lazy(
            "seven_day_streaks_help",
            "Achieve a Pokémon catch streak or PokéStop spin streak of seven days.",
            "Achieve a Pokémon catch streak or PokéStop spin streak of seven days {0} times.",
            100,
        ).format(100),
        stat_id=64,
        bronze=1,
        silver=10,
        gold=50,
        platinum=100,
    )
    # 65
    unique_raid_bosses_defeated: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("unique_raid_bosses_defeated_title", "Rising Star"),
        help_text=npgettext_lazy(
            "unique_raid_bosses_defeated_help",
            "Defeat a Pokémon in a raid.",
            "Defeat {0} different species of Pokémon in raids.",
            150,
        ).format(150),
        stat_id=65,
        bronze=2,
        silver=10,
        gold=50,
        platinum=150,
    )
    # 66
    raids_with_friends: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("raids_with_friends_title", "Rising Star Duo"),
        help_text=npgettext_lazy(
            "raids_with_friends_help",
            "Win a raid with a friend.",
            "Win {0} raids with a friend.",
            2000,
        ).format(2000),
        stat_id=66,
        bronze=10,
        silver=100,
        gold=1000,
        platinum=2000,
    )
    # 67
    pokemon_caught_at_your_lures: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokemon_caught_at_your_lures_title", "Picnicker"),
        help_text=npgettext_lazy(
            "pokemon_caught_at_your_lures_help",
            "Use a Lure Module to help another Trainer catch a Pokémon.",
            "Use a Lure Module to help another Trainer catch {0} Pokémon.",
            1,
        ).format(2500),
        stat_id=67,
        bronze=5,
        silver=25,
        gold=500,
        platinum=2000,
    )
    # 68
    wayfarer: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("wayfarer_title", "Wayfarer"),
        help_text=npgettext_lazy(
            context="wayfarer_help",
            singular="Earn a Wayfarer Agreement",
            plural="Earn {0} Wayfarer Agreements",
            number=1500,
        ).format(1500),
        stat_id=68,
        bronze=50,
        silver=500,
        gold=1000,
        platinum=1500,
    )
    # 69
    total_mega_evos: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("total_mega_evos_title", "Successor"),
        help_text=npgettext_lazy(
            "total_mega_evos_help",
            "Mega Evolve a Pokémon {0} time.",
            "Mega Evolve a Pokémon {0} times.",
            1000,
        ).format(1000),
        stat_id=69,
        bronze=1,
        silver=50,
        gold=500,
        platinum=1000,
    )
    # 70
    unique_mega_evos: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("unique_mega_evos_title", "Mega Evolution Guru"),
        help_text=npgettext_lazy(
            "unique_mega_evos_help",
            "Mega Evolve {0} Pokémon.",
            "Mega Evolve {0} different species of Pokémon.",
            46,
        ).format(46),
        stat_id=70,
        bronze=1,
        silver=24,
        gold=36,
        platinum=46,
    )
    # 72, 77 and 79 seem to be route maker related

    # 73 - Friend Finder
    trainers_referred: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("trainers_referred_title", "Friend Finder"),
        help_text=npgettext_lazy(
            "trainers_referred_help",
            "Refer a Trainer",
            "Refer {0} Trainers",
            20,
        ).format(20),
        stat_id=73,
        bronze=1,
        silver=10,
        gold=20,
        platinum=50,
    )

    # 74 - Come kind of invisible pokestop icon?

    # 76 - Raid Expert
    mvt: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("mvt_title", "Raid Expert"),
        help_text=pgettext_lazy(
            "mvt_help",
            "Made the Raid Battle Trainer Achievements screen {0} times.",
        ).format(200),
        stat_id=76,
        bronze=1,
        silver=50,
        gold=200,
        platinum=500,
    )

    # 79
    pokedex_entries_gen8a: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_entries_gen8a_title", "Hisui"),
        help_text=pgettext_lazy(
            "pokedex_entries_gen8a_help",
            "Register {0} Pokémon first discovered in the Hisui region to the Pokédex.",
        ).format(5),
        validators=[
            MaxValueValidator(7),
        ],
        stat_id=79,
        bronze=1,
        silver=3,
        gold=5,
        platinum=7,
    )
    # 81
    capture_large_pokemon: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("capture_large_pokemon_title", "Jumbo Pokémon Collector"),
        help_text=pgettext_lazy(
            "capture_large_pokemon_help",
            "Catch {0} XXL Pokémon.",
        ).format(100),
        stat_id=81,
        bronze=5,
        silver=25,
        gold=100,
        platinum=500,
    )
    # 82
    capture_small_pokemon: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("capture_small_pokemon_title", "Tiny Pokémon Collector"),
        help_text=pgettext_lazy(
            "capture_small_pokemon_help",
            "Catch {0} XXS Pokémon.",
        ).format(100),
        stat_id=82,
        bronze=5,
        silver=25,
        gold=100,
        platinum=500,
    )

    # 1002
    mini_collection: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("mini_collection_title", "Elite Collector"),
        help_text=pgettext_lazy("mini_collection_help", "Complete Collection Challenges."),
        stat_id=1002,
    )

    # 1003
    butterfly_collector: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("butterfly_collector_title", "Vivillon Collector"),
        help_text=pgettext_lazy(
            "butterfly_collector_help", "Collect Vivillon from all over the world."
        ),
        stat_id=1003,
        validators=[
            MaxValueValidator(18),
        ],
    )

    battle_hub_stats_wins: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_wins", "Wins"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_battles: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_battles", "Battles"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_stardust: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_stardust", "Stardust Earned"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_streak: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_streak", "Longest Streak"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )

    # Type Medals

    type_normal: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_normal_title", "Schoolkid"),
        help_text=pgettext_lazy("type_normal_help", "Catch {0} Normal-type Pokémon.").format(200),
        stat_id=18,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_fighting: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fighting_title", "Black Belt"),
        help_text=pgettext_lazy("type_fighting_help", "Catch {0} Fighting-type Pokémon.").format(
            200
        ),
        stat_id=19,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_flying: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_flying_title", "Bird Keeper"),
        help_text=pgettext_lazy("type_flying_help", "Catch {0} Flying-type Pokémon.").format(200),
        stat_id=20,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_poison: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_poison_title", "Punk Girl"),
        help_text=pgettext_lazy("type_poison_help", "Catch {0} Poison-type Pokémon.").format(200),
        stat_id=21,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_ground: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ground_title", "Ruin Maniac"),
        help_text=pgettext_lazy("type_ground_help", "Catch {0} Ground-type Pokémon.").format(200),
        stat_id=22,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_rock: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_rock_title", "Hiker"),
        help_text=pgettext_lazy("type_rock_help", "Catch {0} Rock-type Pokémon.").format(200),
        stat_id=23,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_bug: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_bug_title", "Bug Catcher"),
        help_text=pgettext_lazy("type_bug_help", "Catch {0} Bug-type Pokémon.").format(200),
        stat_id=24,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_ghost: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ghost_title", "Hex Maniac"),
        help_text=pgettext_lazy("type_ghost_help", "Catch {0} Ghost-type Pokémon.").format(200),
        stat_id=25,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_steel: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_steel_title", "Rail Staff"),
        help_text=pgettext_lazy("type_steel_help", "Catch {0} Steel-type Pokémon.").format(200),
        stat_id=26,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_fire: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fire_title", "Kindler"),
        help_text=pgettext_lazy("type_fire_help", "Catch {0} Fire-type Pokémon.").format(200),
        stat_id=27,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_water: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_water_title", "Swimmer"),
        help_text=pgettext_lazy("type_water_help", "Catch {0} Water-type Pokémon.").format(200),
        stat_id=28,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_grass: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_grass_title", "Gardener"),
        help_text=pgettext_lazy("type_grass_help", "Catch {0} Grass-type Pokémon.").format(200),
        stat_id=29,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_electric: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_electric_title", "Rocker"),
        help_text=pgettext_lazy("type_electric_help", "Catch {0} Electric-type Pokémon.").format(
            200
        ),
        stat_id=30,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_psychic: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_psychic_title", "Psychic"),
        help_text=pgettext_lazy("type_psychic_help", "Catch {0} Psychic-type Pokémon.").format(
            200
        ),
        stat_id=31,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_ice: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_ice_title", "Skier"),
        help_text=pgettext_lazy("type_ice_help", "Catch {0} Ice-type Pokémon.").format(200),
        stat_id=32,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_dragon: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_dragon_title", "Dragon Tamer"),
        help_text=pgettext_lazy("type_dragon_help", "Catch {0} Dragon-type Pokémon.").format(200),
        stat_id=33,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_dark: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_dark_title", "Delinquent"),
        help_text=pgettext_lazy("type_dark_help", "Catch {0} Dark-type Pokémon.").format(200),
        stat_id=34,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )
    type_fairy: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("type_fairy_title", "Fairy Tale Girl"),
        help_text=pgettext_lazy("type_fairy_help", "Catch {0} Fairy-type Pokémon.").format(200),
        stat_id=35,
        bronze=10,
        silver=50,
        gold=200,
        platinum=2500,
    )

    gym_gold: int | None = IntegerStatistic(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("gym_gold_title", "Gold Gym Badges"),
        help_text=pgettext_lazy(
            "gym_gold_help",
            "You can find this by clicking the {gym_list_button} button under the {profile_category_gymbadges} category on your profile in game, and then counting how many are gold.",
        ).format(
            gym_list_button=pgettext_lazy("gym_list_button", "List"),
            profile_category_gymbadges=pgettext_lazy("profile_category_gymbadges", "Gym Badges"),
        ),
        reversable=True,
    )

    def has_modified_extra_fields(self) -> bool:
        return bool(self.modified_extra_fields())

    has_modified_extra_fields.boolean = True

    def modified_extra_fields(self) -> list[str]:
        return [
            field.name
            for field in self.get_stat_fields()
            if field not in STANDARD_OCR_STATS and getattr(self, field.name) is not None
        ]

    def clean(self) -> NoReturn | None:
        if not self.trainer:
            return

        if (
            self.total_xp
            and self.trainer_level
            and self.trainer_level
            not in map(
                lambda x: x.level, (levels := get_possible_levels_from_total_xp(self.total_xp))
            )
        ):
            formatted_levels = ", ".join(map(lambda x: str(x.level), levels))
            raise ValidationError(
                pgettext_lazy(
                    "trainer_level_error",
                    "The Trainer Level is not valid for the entered Total XP. Expected one of {levels}, got {trainer_level}.",
                ).format(levels=formatted_levels, trainer_level=self.trainer_level)
            )
        elif (
            self.total_xp
            and not self.trainer_level
            and len((levels := get_possible_levels_from_total_xp(self.total_xp))) == 1
        ):
            self.trainer_level = levels[0].level

        REQUIRED_FIELDS = Update.get_stat_fields()

        if not any([(getattr(self, field.name) is not None) for field in REQUIRED_FIELDS]):
            raise ValidationError(
                _("You must fill out at least ONE of the following stats.\n{stats}").format(
                    stats=", ".join([str(field.verbose_name) for field in REQUIRED_FIELDS])
                )
            )

        error_dict: defaultdict[str, list[str]] = defaultdict(list)

        AGGREGATES = {
            f"max_{field.name}": models.Max(
                f"update__{field.name}",
                filter=(
                    models.Q(update__update_time__lt=self.update_time)
                    & models.Q(**{f"update__{field.name}__isnull": False})
                ),
            )
            for field in Update.get_non_reversable_fields()
            if bool(new_stat := getattr(self, field.name))
        }

        latest_stats_prior = Trainer.objects.filter(pk=self.trainer.pk).aggregate(**AGGREGATES)

        for field in Update.get_non_reversable_fields():
            if (new_stat := getattr(self, field.name)) is not None:
                if (
                    latest_stat := latest_stats_prior.get(f"max_{field.name}")
                ) is not None and new_stat < latest_stat:
                    error_dict[field.name].append(
                        _(
                            "The new value for {field} is less than the previous value of {latest_stat}.",
                        ).format(field=field.verbose_name, latest_stat=latest_stat)
                    )

        if error_dict:
            raise ValidationError(error_dict)

    class Meta:
        get_latest_by = "update_time"
        ordering = ["-update_time"]
        verbose_name = _("Update")
        verbose_name_plural = _("Updates")

    @classmethod
    def get_stat_fields(cls) -> list[BaseStatistic]:
        return [field for field in cls._meta.get_fields() if isinstance(field, BaseStatistic)]

    @classmethod
    def get_sortable_fields(cls) -> list[BaseStatistic]:
        return [field for field in cls.get_stat_fields() if field.sortable]

    @classmethod
    def get_non_reversable_fields(cls) -> list[BaseStatistic]:
        return [field for field in cls.get_stat_fields() if not field.reversable]


STANDARD_OCR_STATS: list[BaseStatistic] = [
    Update.total_xp.field,
    Update.travel_km.field,
    Update.pokedex_entries.field,
    Update.capture_total.field,
]

STANDARD_MEDALS: list[BaseStatistic] = [
    Update.travel_km.field,
    Update.pokedex_entries.field,
    Update.capture_total.field,
    Update.evolved_total.field,
    Update.hatched_total.field,
    Update.pokestops_visited.field,
    Update.unique_pokestops.field,
    Update.big_magikarp.field,
    Update.battle_attack_won.field,
    Update.battle_training_won.field,
    Update.small_rattata.field,
    Update.pikachu.field,
    Update.unown.field,
    Update.pokedex_entries_gen2.field,
    Update.raid_battle_won.field,
    Update.legendary_battle_won.field,
    Update.berries_fed.field,
    Update.hours_defended.field,
    Update.pokedex_entries_gen3.field,
    Update.challenge_quests.field,
    Update.max_level_friends.field,
    Update.trading.field,
    Update.trading_distance.field,
    Update.pokedex_entries_gen4.field,
    Update.great_league.field,
    Update.ultra_league.field,
    Update.master_league.field,
    Update.photobomb.field,
    Update.pokedex_entries_gen5.field,
    Update.pokemon_purified.field,
    Update.rocket_grunts_defeated.field,
    Update.rocket_giovanni_defeated.field,
    Update.buddy_best.field,
    Update.pokedex_entries_gen6.field,
    Update.pokedex_entries_gen7.field,
    Update.pokedex_entries_gen8.field,
    Update.seven_day_streaks.field,
    Update.unique_raid_bosses_defeated.field,
    Update.raids_with_friends.field,
    Update.pokemon_caught_at_your_lures.field,
    Update.wayfarer.field,
    Update.total_mega_evos.field,
    Update.unique_mega_evos.field,
    Update.trainers_referred.field,
    Update.mvt.field,
    Update.pokedex_entries_gen8a.field,
    Update.capture_large_pokemon.field,
    Update.capture_small_pokemon.field,
]

BATTLE_HUB_STATS: list[BaseStatistic] = [
    Update.battle_hub_stats_wins.field,
    Update.battle_hub_stats_battles.field,
    Update.battle_hub_stats_stardust.field,
    Update.battle_hub_stats_streak.field,
]

UPDATE_FIELDS_TYPES: list[BaseStatistic] = [
    Update.type_normal.field,
    Update.type_fighting.field,
    Update.type_flying.field,
    Update.type_poison.field,
    Update.type_ground.field,
    Update.type_rock.field,
    Update.type_bug.field,
    Update.type_ghost.field,
    Update.type_steel.field,
    Update.type_fire.field,
    Update.type_water.field,
    Update.type_grass.field,
    Update.type_electric.field,
    Update.type_psychic.field,
    Update.type_ice.field,
    Update.type_dragon.field,
    Update.type_dark.field,
    Update.type_fairy.field,
]


@receiver(post_save, sender=Update)
def update_discord_level(
    sender: type[models.Model],
    created: bool = None,
    raw: bool = None,
    instance: Update = None,
    **kwargs,
) -> None:
    if created and not raw and instance.trainer_level:
        membership: DiscordGuildMembership
        for membership in (
            DiscordGuildMembership.objects.select_related("guild")
            .exclude(active=False)
            .filter(
                guild__set_nickname_on_update=True,
                user__user__trainer=instance.trainer,
            )
        ):
            base = membership.nick_override or instance.trainer.nickname

            if membership.guild.level_format == "int":
                ext = str(instance.trainer_level)
            elif membership.guild.level_format == "circled_level":
                ext = circled_level(instance.trainer_level)
            else:
                ext = ""

            if (len(base) + len(ext)) > 32:
                chopped_base = base[slice(0, 32 - len(ext) - 1)]
                combined = f"{chopped_base}…{ext}"
            elif (len(base) + len(ext)) == 32:
                combined = f"{base}{ext}"
            else:
                combined = f"{base} {ext}"

            membership._change_nick(combined)


class ProfileBadge(models.Model):
    slug: str = models.SlugField(db_index=True, primary_key=True)
    title: str = models.CharField(db_index=True, max_length=20)
    description: str = models.CharField(db_index=True, max_length=240)
    badge: models.FieldFile = models.ImageField(upload_to=get_path_for_badges)
    members: models.QuerySet[Trainer] = models.ManyToManyField(
        Trainer,
        through="ProfileBadgeHoldership",
        through_fields=("badge", "trainer"),
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")


class ProfileBadgeHoldership(models.Model):
    trainer: Trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    badge: ProfileBadge = models.ForeignKey(ProfileBadge, on_delete=models.CASCADE)
    awarded_by: Trainer = models.ForeignKey(
        Trainer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="badges_awarded",
    )
    awarded_on: datetime = models.DateTimeField(auto_now_add=True)
    reason_given: str = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.trainer} - {self.badge}"


class Community(models.Model):
    uuid: UUID = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="UUID",
    )
    language: str = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max(settings.LANGUAGES, key=lambda x: len(x[0]))[0]),
    )
    timezone: str = models.CharField(
        default=settings.TIME_ZONE,
        max_length=255,
    )

    name: str = models.CharField(max_length=70)
    description: str | None = models.TextField(null=True, blank=True)
    handle: str = models.SlugField(unique=True)

    privacy_public: bool = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Viewable"),
        help_text=_(
            "By default, this is off." " Turn this on to share your community with the world."
        ),
    )
    privacy_public_join: bool = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Joinable"),
        help_text=_(
            "By default, this is off."
            " Turn this on to make your community free to join."
            " No invites required."
        ),
    )
    privacy_tournaments: bool = models.BooleanField(
        default=False,
        verbose_name=_("Tournament: Publicly Viewable"),
        help_text=_(
            "By default, this is off."
            " Turn this on to share your tournament results with the world."
        ),
    )

    memberships_personal: models.QuerySet[Trainer] = models.ManyToManyField(Trainer, blank=True)
    memberships_discord: models.QuerySet[DiscordGuild] = models.ManyToManyField(
        DiscordGuild,
        through="CommunityMembershipDiscord",
        through_fields=("community", "discord"),
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    def get_members(self) -> models.QuerySet[Trainer]:
        qs = self.memberships_personal.all()

        for x in CommunityMembershipDiscord.objects.filter(sync_members=True, community=self):
            qs |= x.members_queryset()

        return qs

    def get_absolute_url(self) -> str:
        return reverse("trainerdex:leaderboard", kwargs={"community": self.handle})

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")


class CommunityMembershipDiscord(models.Model):
    community: Community = models.ForeignKey(Community, on_delete=models.CASCADE)
    discord: DiscordGuild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)

    sync_members: bool = models.BooleanField(
        default=True,
        help_text=_("Members in this Discord are automatically included in the community."),
    )
    include_roles: models.QuerySet[DiscordRole] = models.ManyToManyField(
        DiscordRole,
        related_name="include_roles_community_membership_discord",
        blank=True,
    )
    exclude_roles: models.QuerySet[DiscordRole] = models.ManyToManyField(
        DiscordRole,
        related_name="exclude_roles_community_membership_discord",
        blank=True,
    )

    def __str__(self) -> str:
        return "{community} - {guild}".format(community=self.community, guild=self.discord)

    def members_queryset(self) -> models.QuerySet[Trainer]:
        if self.sync_members:
            qs = Trainer.objects.exclude(owner__is_active=False).filter(
                owner__socialaccount__guild_memberships__guild__communitymembershipdiscord=self
            )

            if self.include_roles.exists():
                q = models.Q()
                for role in self.include_roles.all():
                    q = q | models.Q(
                        owner__socialaccount__guild_memberships__data__roles__contains=str(role.id)
                    )
                qs = qs.filter(q)

            if self.exclude_roles.exists():
                q = models.Q()
                for role in self.exclude_roles.all():
                    q = q | models.Q(
                        owner__socialaccount__guild_memberships__data__roles__contains=str(role.id)
                    )
                qs = qs.exclude(q)

            return qs
        else:
            return Trainer.objects.none()

    class Meta:
        verbose_name = _("Community Discord Connection")
        verbose_name_plural = _("Community Discord Connections")
