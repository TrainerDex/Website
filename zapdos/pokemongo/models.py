import logging
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Collection, Dict, List, Literal, Tuple, Union

import pytz
from common.models import BaseModel, ExternalUUIDModel, FeedPost
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import npgettext_lazy, pgettext_lazy

from pokemongo.constants import (
    FRIENDSHIPS_RELEASE_DATE,
    GYM_REWORK_DATE,
    LEGENDARY_RAID_RELEASE_DATE,
    POGO_RELEASE_DATE,
    QUESTS_RELEASE_DATE,
    RAID_RELEASE_DATE,
)

logger = logging.getLogger("django.trainerdex")
User = get_user_model()


class Faction(BaseModel):
    class FactionChoices(models.IntegerChoices):
        UNALIGNED = 0, _("Unaligned")
        MYSTIC = 1, _("Mystic")
        VALOR = 2, _("Valor")
        INSTINCT = 3, _("Instinct")

    id = models.SmallIntegerField(
        primary_key=True,
        choices=FactionChoices.choices,
        validators=[
            MinValueValidator(min(FactionChoices.values)),  # 0
            MaxValueValidator(max(FactionChoices.values)),  # 3
        ],
    )
    slug = models.SlugField(
        db_index=True,
        unique=True,
        choices=[(x.lower(), x.lower()) for x in FactionChoices.names],
        max_length=len(max(FactionChoices.names, key=len)),
        null=False,
        editable=False,
    )

    @property
    def name(self) -> str:
        return self.FactionChoices(self.id).label

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        self.slug = self.FactionChoices(self.id).name.lower()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return self.name


class FactionAlliance(ExternalUUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    faction = models.ForeignKey(
        Faction,
        on_delete=models.CASCADE,
    )

    date_aligned = models.DateField(blank=True, null=True)
    date_disbanded = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.faction}"


class DummyFactionAlliance:
    def __init__(self, user: User):
        self.user = user
        self.faction = Faction.objects.get(pk=0)
        self.date_aligned = None
        self.date_disbanded = None

    def __str__(self) -> str:
        return f"{self.user} - {self.faction}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __bool__(self) -> Literal[False]:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (DummyFactionAlliance, type(None)))


class MedalProgressPost(FeedPost):
    total_xp = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("profile_total_xp", "Total XP"),
        validators=[MinValueValidator(100)],
    )

    # Pokedex Figures
    pokedex_caught = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("pokedex_page_caught", "Unique Species Caught"),
        help_text=pgettext_lazy(
            "pokedex_help",
            "You can find this by clicking the {screen_title_pokedex} button in your game. It should then be listed at the top of the screen.",
        ).format(screen_title_pokedex=pgettext_lazy("screen_title_pokedex", "POKÉDEX")),
        validators=[MinValueValidator(1)],
    )
    pokedex_seen = models.PositiveIntegerField(
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
    # Badge_1
    badge_travel_km = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_travel_km_title", "Jogger"),
        help_text=pgettext_lazy("badge_travel_km", "Walk {0:0,g} km.").format(10000.0),
        validators=[MinValueValidator(Decimal(0.0))],
    )
    # Badge_2
    badge_pokedex_entries = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_title", "Kanto"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries", "Register {0} Kanto region Pokémon in the Pokédex."
        ).format(151),
        validators=[MaxValueValidator(151), MinValueValidator(1)],
    )
    # Badge_3
    badge_capture_total = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_capture_total_title", "Collector"),
        help_text=pgettext_lazy("badge_capture_total", "Catch {0} Pokémon.").format(50000),
        validators=[MinValueValidator(1)],
    )
    # Badge_5
    badge_evolved_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_evolved_total_title", "Scientist"),
        help_text=pgettext_lazy("badge_evolved_total", "Evolve {0} Pokémon.").format(2000),
    )
    # Badge_6
    badge_hatched_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_hatched_total_title", "Breeder"),
        help_text=pgettext_lazy("badge_hatched_total", "Hatch {0} eggs.").format(2500),
    )
    # Badge_8
    badge_pokestops_visited = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokestops_visited_title", "Backpacker"),
        help_text=pgettext_lazy("badge_pokestops_visited", "Visit {0} PokéStops.").format(50000),
    )
    # Badge_9
    badge_unique_pokestops = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_unique_pokestops_title", "Sightseer"),
        help_text=npgettext_lazy(
            "badge_unique_pokestops",
            "Visit a PokéStop.",
            "Visit {0} unique PokéStops.",
            2000,
        ).format(2000),
    )
    # Badge_11
    badge_big_magikarp = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_big_magikarp_title", "Fisher"),
        help_text=pgettext_lazy("badge_big_magikarp", "Catch {0} big Magikarp.").format(1000),
    )
    # Badge_13
    badge_battle_attack_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_battle_attack_won_title", "Battle Girl"),
        help_text=pgettext_lazy("badge_battle_attack_won", "Win {0} Gym battles.").format(4000),
    )
    # Badge_14
    badge_battle_training_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_battle_training_won_title", "Ace Trainer"),
        help_text=pgettext_lazy("badge_battle_training_won", "Train {0} times.").format(2000),
    )
    # Badge_36
    badge_small_rattata = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_small_rattata_title", "Youngster"),
        help_text=pgettext_lazy("badge_small_rattata", "Catch {0} tiny Rattata.").format(1000),
    )
    # Badge_37
    badge_pikachu = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pikachu_title", "Pikachu Fan"),
        help_text=pgettext_lazy("badge_pikachu", "Catch {0} Pikachu.").format(1000),
    )
    # Badge_38
    badge_unown = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_unown_title", "Unown"),
        help_text=pgettext_lazy("badge_unown", "Catch {0} Unown.").format(28),
        validators=[
            MaxValueValidator(28),
        ],
    )
    # Badge_39
    badge_pokedex_entries_gen2 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen2_title", "Johto"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen2",
            "Register {0} Pokémon first discovered in the Johto region to the Pokédex.",
        ).format(100),
        validators=[
            MaxValueValidator(100),
        ],
    )
    # Badge_40
    badge_raid_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_raid_battle_won_title", "Champion"),
        help_text=pgettext_lazy("badge_raid_battle_won", "Win {0} raids.").format(2000),
    )
    # Badge_41
    badge_legendary_battle_won = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_legendary_battle_won_title", "Battle Legend"),
        help_text=pgettext_lazy("badge_legendary_battle_won", "Win {0} Legendary raids.").format(
            2000
        ),
    )
    # Badge_42
    badge_berries_fed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_berries_fed_title", "Berry Master"),
        help_text=pgettext_lazy("badge_berries_fed", "Feed {0} Berries at Gyms.").format(15000),
    )
    # Badge_43
    badge_hours_defended = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_hours_defended_title", "Gym Leader"),
        help_text=pgettext_lazy("badge_hours_defended", "Defend Gyms for {0} hours.").format(
            15000
        ),
    )
    # Badge_45
    badge_pokedex_entries_gen3 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen3_title", "Hoenn"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen3",
            "Register {0} Pokémon first discovered in the Hoenn region to the Pokédex.",
        ).format(135),
        validators=[
            MaxValueValidator(135),
        ],
    )
    # Badge_46
    badge_challenge_quests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_challenge_quests_title", "Pokémon Ranger"),
        help_text=pgettext_lazy(
            "badge_challenge_quests", "Complete {0} Field Research tasks."
        ).format(2500),
    )
    # Badge_48
    badge_max_level_friends = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_max_level_friends_title", "Idol"),
        help_text=npgettext_lazy(
            context="badge_max_level_friends",
            singular="Become Best Friends with {0} Trainer.",
            plural="Become Best Friends with {0} Trainers.",
            number=20,
        ).format(20),
    )
    # Badge_49
    badge_trading = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_trading_title", "Gentleman"),
        help_text=pgettext_lazy("badge_trading", "Trade {0} Pokémon.").format(2500),
    )
    # Badge_50
    badge_trading_distance = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_trading_distance_title", "Pilot"),
        help_text=pgettext_lazy(
            "badge_trading_distance",
            "Earn {0} km across the distance of all Pokémon trades.",
        ).format(10000000),
    )
    # Badge_51
    badge_pokedex_entries_gen4 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen4__title", "Sinnoh"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen4",
            "Register {0} Pokémon first discovered in the Sinnoh region to the Pokédex.",
        ).format(107),
        validators=[
            MaxValueValidator(107),
        ],
    )
    # Badge_52
    badge_great_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_great_league_title", "Great League Veteran"),
        help_text=npgettext_lazy(
            context="badge_great_league",
            singular="Win a Trainer Battle in the Great League.",
            plural="Win {0} Trainer Battles in the Great League.",
            number=1000,
        ).format(1000),
    )
    # Badge_53
    badge_ultra_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_ultra_league_title", "Ultra League Veteran"),
        help_text=npgettext_lazy(
            context="badge_ultra_league",
            singular="Win a Trainer Battle in the Ultra League.",
            plural="Win {0} Trainer Battles in the Ultra League.",
            number=1000,
        ).format(1000),
    )
    # Badge_54
    badge_master_league = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_master_league_title", "Master League Veteran"),
        help_text=npgettext_lazy(
            context="badge_master_league",
            singular="Win a Trainer Battle in the Master League.",
            plural="Win {0} Trainer Battles in the Master League.",
            number=1000,
        ).format(1000),
    )
    # Badge_55
    badge_photobomb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_photobomb_title", "Cameraman"),
        help_text=npgettext_lazy(
            context="badge_photobomb",
            singular="Have {0} surprise encounter in GO Snapshot.",
            plural="Have {0} surprise encounters in GO Snapshot.",
            number=400,
        ).format(400),
    )
    # Badge_56
    badge_pokedex_entries_gen5 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen5__title", "Unova"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen5",
            "Register {0} Pokémon first discovered in the Unova region to the Pokédex.",
        ).format(156),
        validators=[
            MaxValueValidator(156),
        ],
    )
    # Badge_57
    badge_pokemon_purified = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokemon_purified_title", "Purifier"),
        help_text=pgettext_lazy("badge_pokemon_purified", "Purify {0} Shadow Pokémon.").format(
            1000
        ),
    )
    # Badge_58
    badge_rocket_grunts_defeated = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_rocket_grunts_defeated_title", "Hero"),
        help_text=pgettext_lazy(
            "badge_rocket_grunts_defeated", "Defeat {0} Team GO Rocket Grunts."
        ).format(2000),
    )
    # Badge_59
    badge_rocket_giovanni_defeated = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_rocket_giovanni_defeated_title", "Ultra Hero"),
        help_text=npgettext_lazy(
            context="badge_rocket_giovanni_defeated",
            singular="Defeat the Team GO Rocket Boss.",
            plural="Defeat the Team GO Rocket Boss {0} times. ",
            number=50,
        ).format(50),
    )
    # Badge_60
    badge_buddy_best = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_buddy_best_title", "Best Buddy"),
        help_text=npgettext_lazy(
            context="badge_buddy_best",
            singular="Have 1 Best Buddy.",
            plural="Have {0} Best Buddies.",
            number=200,
        ).format(200),
    )
    # Badge_61
    badge_pokedex_entries_gen6 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen6__title", "Kalos"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen6",
            "Register {0} Pokémon first discovered in the Kalos region to the Pokédex.",
        ).format(72),
        validators=[
            MaxValueValidator(72),
        ],
    )
    # Badge_62
    badge_pokedex_entries_gen7 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen7__title", "Alola"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen7",
            "Register {0} Pokémon first discovered in the Alola region to the Pokédex.",
        ).format(88),
        validators=[
            MaxValueValidator(88),
        ],
    )
    # Badge_63
    badge_pokedex_entries_gen8 = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokedex_entries_gen8__title", "Galar"),
        help_text=pgettext_lazy(
            "badge_pokedex_entries_gen8",
            "Register {0} Pokémon first discovered in the Alola region to the Pokédex.",
        ).format(89),
        validators=[
            MaxValueValidator(89),
        ],
    )
    # Badge_64
    badge_7_day_streaks = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_7_day_streaks_title", "Triathlete"),
        help_text=npgettext_lazy(
            "badge_7_day_streaks",
            "Achieve a Pokémon catch streak or PokéStop spin streak of seven days.",
            "Achieve a Pokémon catch streak or PokéStop spin streak of seven days {0} times.",
            100,
        ).format(100),
    )
    # Badge_65
    badge_unique_raid_bosses_defeated = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_unique_raid_bosses_defeated_title", "Rising Star"),
        help_text=npgettext_lazy(
            "badge_unique_raid_bosses_defeated",
            "Defeat a Pokémon in a raid.",
            "Defeat {0} different species of Pokémon in raids.",
            150,
        ).format(150),
    )
    # Badge_66
    badge_raids_with_friends = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_raids_with_friends_title", "Rising Star Duo"),
        help_text=npgettext_lazy(
            "badge_raids_with_friends",
            "Win a raid with a friend.",
            "Win {0} raids with a friend.",
            2000,
        ).format(2000),
    )
    # Badge_67
    badge_pokemon_caught_at_your_lures = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_pokemon_caught_at_your_lures_title", "Picnicker"),
        help_text=npgettext_lazy(
            "badge_pokemon_caught_at_your_lures",
            "Use a Lure Module to help another Trainer catch a Pokémon.",
            "Use a Lure Module to help another Trainer catch {0} Pokémon.",
            1,
        ).format(2500),
    )
    # Badge_68
    badge_wayfarer = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_wayfarer_title", "Wayfarer"),
        help_text=npgettext_lazy(
            context="badge_wayfarer",
            singular="Earn a Wayfarer Agreement",
            plural="Earn {0} Wayfarer Agreements",
            number=1500,
        ).format(1500),
    )
    # Badge_69
    badge_total_mega_evos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_total_mega_evos_title", "Successor"),
        help_text=npgettext_lazy(
            "badge_total_mega_evos",
            "Mega Evolve a Pokémon {0} time.",
            "Mega Evolve a Pokémon {0} times.",
            1000,
        ).format(1000),
    )
    # Badge_70
    badge_unique_mega_evos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_unique_mega_evos_title", "Mega Evolution Guru"),
        help_text=npgettext_lazy(
            "badge_unique_mega_evos",
            "Mega Evolve {0} Pokémon.",
            "Mega Evolve {0} different species of Pokémon.",
            46,
        ).format(46),
    )

    # Type Medals

    badge_type_normal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_normal_title", "Schoolkid"),
        help_text=pgettext_lazy("badge_type_normal", "Catch {0} Normal-type Pokémon.").format(200),
    )
    badge_type_fighting = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fighting_title", "Black Belt"),
        help_text=pgettext_lazy("badge_type_fighting", "Catch {0} Fighting-type Pokémon.").format(
            200
        ),
    )
    badge_type_flying = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_flying_title", "Bird Keeper"),
        help_text=pgettext_lazy("badge_type_flying", "Catch {0} Flying-type Pokémon.").format(200),
    )
    badge_type_poison = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_poison_title", "Punk Girl"),
        help_text=pgettext_lazy("badge_type_poison", "Catch {0} Poison-type Pokémon.").format(200),
    )
    badge_type_ground = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ground_title", "Ruin Maniac"),
        help_text=pgettext_lazy("badge_type_ground", "Catch {0} Ground-type Pokémon.").format(200),
    )
    badge_type_rock = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_rock_title", "Hiker"),
        help_text=pgettext_lazy("badge_type_rock", "Catch {0} Rock-type Pokémon.").format(200),
    )
    badge_type_bug = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_bug_title", "Bug Catcher"),
        help_text=pgettext_lazy("badge_type_bug", "Catch {0} Bug-type Pokémon.").format(200),
    )
    badge_type_ghost = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ghost_title", "Hex Maniac"),
        help_text=pgettext_lazy("badge_type_ghost", "Catch {0} Ghost-type Pokémon.").format(200),
    )
    badge_type_steel = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_steel_title", "Rail Staff"),
        help_text=pgettext_lazy("badge_type_steel", "Catch {0} Steel-type Pokémon.").format(200),
    )
    badge_type_fire = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fire_title", "Kindler"),
        help_text=pgettext_lazy("badge_type_fire", "Catch {0} Fire-type Pokémon.").format(200),
    )
    badge_type_water = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_water_title", "Swimmer"),
        help_text=pgettext_lazy("badge_type_water", "Catch {0} Water-type Pokémon.").format(200),
    )
    badge_type_grass = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_grass_title", "Gardener"),
        help_text=pgettext_lazy("badge_type_grass", "Catch {0} Grass-type Pokémon.").format(200),
    )
    badge_type_electric = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_electric_title", "Rocker"),
        help_text=pgettext_lazy("badge_type_electric", "Catch {0} Electric-type Pokémon.").format(
            200
        ),
    )
    badge_type_psychic = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_psychic_title", "Psychic"),
        help_text=pgettext_lazy("badge_type_psychic", "Catch {0} Psychic-type Pokémon.").format(
            200
        ),
    )
    badge_type_ice = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_ice_title", "Skier"),
        help_text=pgettext_lazy("badge_type_ice", "Catch {0} Ice-type Pokémon.").format(200),
    )
    badge_type_dragon = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_dragon_title", "Dragon Tamer"),
        help_text=pgettext_lazy("badge_type_dragon", "Catch {0} Dragon-type Pokémon.").format(200),
    )
    badge_type_dark = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_dark_title", "Delinquent"),
        help_text=pgettext_lazy("badge_type_dark", "Catch {0} Dark-type Pokémon.").format(200),
    )
    badge_type_fairy = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("badge_type_fairy_title", "Fairy Tale Girl"),
        help_text=pgettext_lazy("badge_type_fairy", "Catch {0} Fairy-type Pokémon.").format(200),
    )

    def validate_fields(
        self,
        errors: Union[None, Dict[str, List[ValidationError]]] = None,
        warnings: Union[None, Dict[str, List[ValidationError]]] = None,
        exclude: Union[None, Collection[str]] = None,
    ) -> Tuple[Dict[str, ValidationError], Dict[str, ValidationError]]:
        """
        Validate all fields and retuns two dicts of all validation errors if any occur.
        """

        if errors is None:
            errors = defaultdict(list)
        if warnings is None:
            warnings = defaultdict(list)
        if exclude is None:
            exclude = []

        start_date: Union[None, date] = self.user.pogo_date_created
        start_or_release: date = self.user.pogo_date_created or POGO_RELEASE_DATE

        field_validation_logic = {
            "total_xp": {"validate": True, "relevant_date": start_date, "daily_limit": 10_000_000},
            "badge_travel_km": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": Decimal(60),
            },
            "badge_capture_total": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 800,
            },
            "badge_evolved_total": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 250,
            },
            "badge_hatched_total": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 60,
            },
            "badge_pokestops_visited": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 500,
            },
            "badge_big_magikarp": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 25,
            },
            "badge_battle_attack_won": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 500,
            },
            "badge_small_rattata": {
                "validate": True,
                "relevant_date": start_date,
                "daily_limit": 25,
            },
            "badge_pikachu": {"validate": True, "relevant_date": start_date, "daily_limit": 200},
            "badge_berries_fed": {
                "validate": True,
                "relevant_date": max(GYM_REWORK_DATE, start_or_release),
                "daily_limit": 3200,
            },
            "badge_hours_defended": {
                "validate": True,
                "relevant_date": max(GYM_REWORK_DATE, start_or_release),
                "daily_limit": 480,
            },
            "badge_raid_battle_won": {
                "validate": True,
                "relevant_date": max(RAID_RELEASE_DATE, start_or_release),
                "daily_limit": 100,
            },
            "badge_legendary_battle_won": {
                "validate": True,
                "relevant_date": max(LEGENDARY_RAID_RELEASE_DATE, start_or_release),
                "daily_limit": 100,
            },
            "badge_challenge_quests": {
                "validate": True,
                "relevant_date": max(QUESTS_RELEASE_DATE, start_or_release),
                "daily_limit": 500,
            },
            "badge_trading": {
                "validate": True,
                "relevant_date": max(FRIENDSHIPS_RELEASE_DATE, start_or_release),
                "daily_limit": 200,
            },
            "badge_trading_distance": {
                "validate": True,
                "relevant_date": max(FRIENDSHIPS_RELEASE_DATE, start_or_release),
                "daily_limit": 1_920_000,
            },
        }

        def within_daily_limit(
            self: MedalProgressUpdate,
            field_name: str,
            relevant_date: Union[date, None],
            limit: Union[int, Decimal],
            other_value: Union[int, Decimal] = 0,
        ) -> bool:
            if (relevant_date is None) or (getattr(self, field_name) is None):
                return True  # No date or no value, so no erro
            days = int((self.post_dt.date() - relevant_date).total_seconds() / 86400)
            progress: Decimal = Decimal(getattr(self, field_name)) - Decimal(other_value)
            daily_rate: Decimal = progress / days
            return daily_rate <= limit

        for field in self._meta.get_fields():
            if (field.name in exclude) or (getattr(self, field.name) is None):
                continue

            # Get latest update with that field present, only get the important fields.
            last_post: Union[None, MedalProgressUpdate] = (
                self.user.medalprogressupdate_set.filter(post_dt__lt=self.post_dt)
                .exclude(**{field.name: None})
                .order_by("-" + field.name, "-post_dt")
                .only(field.name, "post_dt")
                .first()
            )

            # Value must be higher than or equal to than previous value
            if last_post is not None:
                if getattr(self, field.name) < getattr(last_post, field.name):
                    errors[field.name].append(
                        ValidationError(
                            _(
                                "This value has previously been entered at a higher value. ({value}, {datetime})"
                                " Please try again ensuring the value you entered was correct."
                            ).format(
                                value=getattr(last_post, field.name),
                                datetime=last_post.post_dt,
                            )
                        )
                    )

            # If the daily limit since the earlier date is exceeded
            # the second one will also be exceeded, so only check once.
            if field_validation_logic.get(field.name, {}).get("validate", False):
                if (
                    not within_daily_limit(
                        self,
                        field.name,
                        field_validation_logic.get(field.name, {}).get("relevant_date"),
                        field_validation_logic.get(field.name, {}).get("daily_limit"),
                    )
                ) or (
                    (last_post is not None)
                    and not within_daily_limit(
                        self,
                        field.name,
                        getattr(last_post, "post_dt"),
                        field_validation_logic.get(field.name, {}).get("daily_limit"),
                        getattr(last_post, field.name),
                    )
                ):
                    warnings[field.name].append(
                        ValidationError(
                            _(
                                "The value for {medal} may be too high."
                                " Please check for typos and other mistakes."
                            ).format(medal=field.verbose_name)
                        )
                    )

        return errors, warnings

    def clean_fields(self, exclude: Union[None, Collection[str]] = None) -> None:
        """
        Clean all fields and raise a ValidationError containing a dict
        of all validation errors if any occur.
        """
        if exclude is None:
            exclude = []

        errors, _ = self.validate_fields(exclude=exclude)
        if errors:
            raise ValidationError(errors)

        return super().clean_fields(exclude=exclude)


class BattleHubPost(FeedPost):
    battle_hub_stats_wins = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_wins", "Wins"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_battles = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_battles", "Battles"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_stardust = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_stardust", "Stardust Earned"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )
    battle_hub_stats_streak = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=pgettext_lazy("battle_hub_stats_streak", "Longest Streak"),
        help_text=pgettext_lazy(
            "battle_hub_help",
            "You can find this by clicking the {screen_title_battle_hub} button in your game.",
        ).format(screen_title_battle_hub=pgettext_lazy("screen_title_battle_hub", "Battle")),
    )


class GymBadgePost(FeedPost):
    gold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Gold Gym Badges"),
        help_text=pgettext_lazy(
            "gymbadges_gold_help",
            "You can find this by clicking the {gym_badge_list_button} button under the {profile_category_gymbadges} category on your profile in game, and then counting how many are gold.",
        ).format(
            gym_badge_list_button=pgettext_lazy("gym_badge_list_button", "List"),
            profile_category_gymbadges=pgettext_lazy("profile_category_gymbadges", "Gym Badges"),
        ),
        validators=[MaxValueValidator(1000)],
    )


class Community(ExternalUUIDModel):
    language = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max([x[0] for x in settings.LANGUAGES], key=len)),
    )
    timezone = models.CharField(
        max_length=len(max(pytz.common_timezones, key=len)),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_("The timezone of the user"),
    )
    name = models.CharField(max_length=70)
    description = models.TextField(null=True, blank=True)
    handle = models.SlugField(unique=True)

    privacy_public = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Viewable"),
        help_text=_(
            "By default, this is off." " Turn this on to share your community with the world."
        ),
    )
    privacy_public_join = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Joinable"),
        help_text=_(
            "By default, this is off."
            " Turn this on to make your community free to join."
            " No invites required."
        ),
    )
    privacy_tournaments = models.BooleanField(
        default=False,
        verbose_name=_("Tournament: Publicly Viewable"),
        help_text=_(
            "By default, this is off."
            " Turn this on to share your tournament results with the world."
        ),
    )

    memberships = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_members(self):
        qs = self.memberships.all()

        return qs

    def get_absolute_url(self):
        return reverse("trainerdex:leaderboard", kwargs={"community": self.handle})

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")
