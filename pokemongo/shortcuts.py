from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from distutils.util import strtobool
from typing import (
    TYPE_CHECKING,
    Collection,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    TypeVar,
)

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import pgettext as _

if TYPE_CHECKING:
    from pokemongo.models import Trainer, Update

T = TypeVar("T")


def strtoboolornone(value: str) -> Literal[0, 1] | None:
    try:
        return strtobool(value)
    except (ValueError, AttributeError):
        return None


def filter_leaderboard_qs(queryset: QuerySet[Trainer], d: date | None = None) -> QuerySet[Trainer]:
    d = d or timezone.now().date()
    return (
        queryset.exclude(owner__is_active=False)
        .exclude(statistics=False)
        .exclude(update__isnull=True)
        .exclude(verified=False)
        .exclude(last_cheated__gte=d - timedelta(weeks=26))
    )


def filter_leaderboard_qs__update(
    queryset: QuerySet[Update],
    d: date | None = None,
) -> QuerySet[Update]:
    d = d or timezone.now().date()
    return (
        queryset.exclude(trainer__owner__is_active=False)
        .exclude(trainer__statistics=False)
        .exclude(trainer__verified=False)
        .exclude(
            update_time__lt=(
                timezone.now() - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
            )
        )
        .exclude(trainer__last_cheated__gte=d - timedelta(weeks=26))
    )


@dataclass
class Level:
    level: int
    total_xp: int
    xp_required: int | None = None
    quest_requirements: Iterable[Mapping[str, str]] | None = None

    def requirements_to_reach(self) -> dict[str, int | dict[str, str] | None]:
        return {"total_xp": self.total_xp, "quests": self.quest_requirements}

    @property
    def needs_quests(self) -> bool:
        return self.quest_requirements is not None

    def __str__(self) -> str:
        level_term = _("profile_player_level", "Level")
        return f"{level_term} {self.level}"

    def id(self) -> int:
        return self.level


LEVELS: Collection[Level] = [
    Level(level=1, total_xp=0, xp_required=1000),
    Level(level=2, total_xp=1000, xp_required=2000),
    Level(level=3, total_xp=3000, xp_required=3000),
    Level(level=4, total_xp=6000, xp_required=4000),
    Level(level=5, total_xp=10_000, xp_required=5000),
    Level(level=6, total_xp=15_000, xp_required=6000),
    Level(level=7, total_xp=21_000, xp_required=7000),
    Level(level=8, total_xp=28_000, xp_required=8000),
    Level(level=9, total_xp=36_000, xp_required=9000),
    Level(level=10, total_xp=45_000, xp_required=10_000),
    Level(level=11, total_xp=55_000, xp_required=10_000),
    Level(level=12, total_xp=65_000, xp_required=10_000),
    Level(level=13, total_xp=75_000, xp_required=10_000),
    Level(level=14, total_xp=85_000, xp_required=15_000),
    Level(level=15, total_xp=100_000, xp_required=20_000),
    Level(level=16, total_xp=120_000, xp_required=20_000),
    Level(level=17, total_xp=140_000, xp_required=20_000),
    Level(level=18, total_xp=160_000, xp_required=25_000),
    Level(level=19, total_xp=185_000, xp_required=25_000),
    Level(level=20, total_xp=210_000, xp_required=50_000),
    Level(level=21, total_xp=260_000, xp_required=75_000),
    Level(level=22, total_xp=335_000, xp_required=100_000),
    Level(level=23, total_xp=435_000, xp_required=125_000),
    Level(level=24, total_xp=560_000, xp_required=150_000),
    Level(level=25, total_xp=710_000, xp_required=190_000),
    Level(level=26, total_xp=900_000, xp_required=200_000),
    Level(level=27, total_xp=1_100_000, xp_required=250_000),
    Level(level=28, total_xp=1_350_000, xp_required=300_000),
    Level(level=29, total_xp=1_650_000, xp_required=350_000),
    Level(level=30, total_xp=2_000_000, xp_required=500_000),
    Level(level=31, total_xp=2_500_000, xp_required=500_000),
    Level(level=32, total_xp=3_000_000, xp_required=750_000),
    Level(level=33, total_xp=3_750_000, xp_required=1_000_000),
    Level(level=34, total_xp=4_750_000, xp_required=1_250_000),
    Level(level=35, total_xp=6_000_000, xp_required=1_500_000),
    Level(level=36, total_xp=7_500_000, xp_required=2_000_000),
    Level(level=37, total_xp=9_500_000, xp_required=2_500_000),
    Level(level=38, total_xp=12_000_000, xp_required=3_000_000),
    Level(level=39, total_xp=15_000_000, xp_required=5_000_000),
    Level(level=40, total_xp=20_000_000, xp_required=6_000_000),
    Level(level=41, total_xp=26_000_000, xp_required=7_500_000),
    Level(level=42, total_xp=33_500_000, xp_required=9_000_000),
    Level(level=43, total_xp=42_500_000, xp_required=11_000_000),
    Level(level=44, total_xp=53_500_000, xp_required=13_000_000),
    Level(level=45, total_xp=66_500_000, xp_required=15_500_000),
    Level(level=46, total_xp=82_000_000, xp_required=18_000_000),
    Level(level=47, total_xp=100_000_000, xp_required=21_000_000),
    Level(level=48, total_xp=121_000_000, xp_required=25_000_000),
    Level(level=49, total_xp=146_000_000, xp_required=30_000_000),
    Level(level=50, total_xp=176_000_000, xp_required=None),
]


def get_possible_levels_from_total_xp(xp: int) -> Iterable[Level]:
    if xp < LEVELS[40].total_xp:
        possible_levels = [
            x
            for x in filter(
                lambda x: x.total_xp <= xp
                and (x.total_xp + x.xp_required > xp if x.xp_required else True),
                LEVELS,
            )
        ]
    else:
        possible_levels = [
            x
            for x in filter(
                lambda x: 20_000_000 <= x.total_xp <= xp,
                LEVELS,
            )
        ]

    return possible_levels


def get_level(level: int) -> Level:
    if level <= len(LEVELS):
        return LEVELS[level - 1]
    else:
        raise ValueError


OLD_NEW_STAT_MAP = {
    "badge_travel_km": "travel_km",
    "bagde_pokedex_entries": "pokedex_entries",
    "badge_capture_total": "capture_total",
    "badge_evolved_total": "evolved_total",
    "badge_hatched_total": "hatched_total",
    "badge_pokestops_visited": "pokestops_visited",
    "badge_unique_pokestops": "unique_pokestops",
    "badge_big_magikarp": "big_magikarp",
    "badge_battle_attack_won": "battle_attack_won",
    "badge_battle_training_won": "battle_training_won",
    "badge_small_rattata": "small_rattata",
    "badge_pikachu": "pikachu",
    "badge_unown": "unown",
    "badge_pokedex_entries_gen2": "pokedex_entries_gen2",
    "badge_raid_battle_won": "raid_battle_won",
    "badge_legendary_battle_won": "legendary_battle_won",
    "badge_berries_fed": "berries_fed",
    "badge_hours_defended": "hours_defended",
    "badge_pokedex_entries_gen3": "pokedex_entries_gen3",
    "badge_challenge_quests": "challenge_quests",
    "badge_max_level_friends": "max_level_friends",
    "badge_trading": "trading",
    "badge_trading_distance": "trading_distance",
    "badge_pokedex_entries_gen4": "pokedex_entries_gen4",
    "badge_great_league": "great_league",
    "badge_ultra_league": "ultra_league",
    "badge_master_league": "master_league",
    "badge_photobomb": "photobomb",
    "badge_pokedex_entries_gen5": "pokedex_entries_gen5",
    "badge_pokemon_purified": "pokemon_purified",
    "badge_rocket_grunts_defeated": "rocket_grunts_defeated",
    "badge_rocket_giovanni_defeated": "rocket_giovanni_defeated",
    "badge_buddy_best": "buddy_best",
    "badge_pokedex_entries_gen6": "pokedex_entries_gen6",
    "badge_pokedex_entries_gen7": "pokedex_entries_gen7",
    "badge_pokedex_entries_gen8": "pokedex_entries_gen8",
    "badge_seven_day_streaks": "seven_day_streaks",
    "badge_unique_raid_bosses_defeated": "unique_raid_bosses_defeated",
    "badge_raids_with_friends": "raids_with_friends",
    "badge_pokemon_caught_at_your_lures": "pokemon_caught_at_your_lures",
    "badge_wayfarer": "wayfarer",
    "badge_total_mega_evos": "total_mega_evos",
    "badge_unique_mega_evos": "unique_mega_evos",
    "badge_mvt": "mvt",
    "badge_mini_collection": "mini_collection",
    "badge_battle_hub_stats_wins": "battle_hub_stats_wins",
    "badge_type_normal": "type_normal",
    "badge_type_fighting": "type_fighting",
    "badge_type_flying": "type_flying",
    "badge_type_poison": "type_poison",
    "badge_type_ground": "type_ground",
    "badge_type_rock": "type_rock",
    "badge_type_bug": "type_bug",
    "badge_type_ghost": "type_ghost",
    "badge_type_steel": "type_steel",
    "badge_type_fire": "type_fire",
    "badge_type_water": "type_water",
    "badge_type_grass": "type_grass",
    "badge_type_electric": "type_electric",
    "badge_type_psychic": "type_psychic",
    "badge_type_ice": "type_ice",
    "badge_type_dragon": "type_dragon",
    "badge_type_dark": "type_dark",
    "badge_type_fairy": "type_fairy",
    "gymbadges_gold": "gym_gold",
}


def circled_level(i: int) -> str:
    numbers = [
        9312,
        9313,
        9314,
        9315,
        9316,
        9317,
        9318,
        9319,
        9320,
        9321,
        9322,
        9323,
        9324,
        9325,
        9326,
        9327,
        9328,
        9329,
        9330,
        9331,
        12881,
        12882,
        12883,
        12884,
        12885,
        12886,
        12887,
        12888,
        12889,
        12890,
        12891,
        12892,
        12893,
        12894,
        12895,
        12977,
        12978,
        12979,
        12980,
        12981,
        12982,
        12983,
        12984,
        12985,
        12986,
        12987,
        12988,
        12989,
        12990,
        12991,
    ]

    if i <= 0:
        return ""
    try:
        return chr(numbers[i - 1])
    except IndexError:
        return ""


def chunks(iterable: Iterable[T], size: int) -> Iterator[Iterable[T]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]
