from datetime import date, timedelta
from distutils.util import strtobool
from typing import Dict, List, Optional, Union

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import pgettext as _


def strtoboolornone(value) -> Union[bool, None]:
    try:
        return strtobool(value)
    except (ValueError, AttributeError):
        return None


def filter_leaderboard_qs(queryset, d: date = None):
    return (
        queryset.exclude(owner__is_active=False)
        .exclude(statistics=False)
        .exclude(update__isnull=True)
        .exclude(verified=False)
        .exclude(last_cheated__gte=timedelta(weeks=26))
    )


def filter_leaderboard_qs__update(queryset, d: date = None):
    return (
        queryset.exclude(trainer__owner__is_active=False)
        .exclude(trainer__statistics=False)
        .exclude(trainer__verified=False)
        .exclude(
            post_dt__lt=(
                timezone.now() - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
            )
        )
        .exclude(trainer__last_cheated__gte=timedelta(weeks=26))
    )


class Level:
    def __init__(
        self,
        level: int,
        total_xp: int,
        xp_required: Optional[int] = None,
        quest_requirements: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.level = level
        self.total_xp = total_xp
        self.xp_required = xp_required
        self.quest_requirements = quest_requirements

    def requirements_to_reach(self) -> Dict[str, Union[int, Dict[str, str]]]:
        return {"total_xp": self.total_xp, "quests": self.quest_requirements}

    @property
    def needs_quests(self) -> bool:
        return self.quest_requirements is not None

    def __str__(self) -> str:
        level_term = _("profile_player_level", "Level")
        return f"{level_term} {self.level}"

    def id(self) -> int:
        return self.level


LEVELS: List[Level] = [
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


def get_possible_levels_from_total_xp(xp: int) -> List[Level]:
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


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
