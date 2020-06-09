from collections import namedtuple
from distutils.util import strtobool
from django.db.models.query import QuerySet

def strtoboolornone(value: str, default: bool=None) -> bool:
    try:
        return strtobool(value)
    except ValueError:
        return default

def filter_leaderboard_qs(queryset: QuerySet) -> QuerySet:
    return queryset.exclude(owner__is_active=False) \
        .exclude(user__gdpr=False) \
        .exclude(user__banned=True) \
        .exclude(verified=False) \
        .exclude(update__isnull=True)

def level_parser(xp=None, level=None):
    """
    Takes either xp OR level and returns the value for the other
    """
    
    LevelTuple = namedtuple('LevelTuple', ['level','total_xp','xp_required'])
    LevelTuples = [
        LevelTuple(level=1,total_xp=0,xp_required=1000),
        LevelTuple(level=2,total_xp=1000,xp_required=2000),
        LevelTuple(level=3,total_xp=3000,xp_required=3000),
        LevelTuple(level=4,total_xp=6000,xp_required=4000),
        LevelTuple(level=5,total_xp=10000,xp_required=5000),
        LevelTuple(level=6,total_xp=15000,xp_required=6000),
        LevelTuple(level=7,total_xp=21000,xp_required=7000),
        LevelTuple(level=8,total_xp=28000,xp_required=8000),
        LevelTuple(level=9,total_xp=36000,xp_required=9000),
        LevelTuple(level=10,total_xp=45000,xp_required=10000),
        LevelTuple(level=11,total_xp=55000,xp_required=10000),
        LevelTuple(level=12,total_xp=65000,xp_required=10000),
        LevelTuple(level=13,total_xp=75000,xp_required=10000),
        LevelTuple(level=14,total_xp=85000,xp_required=15000),
        LevelTuple(level=15,total_xp=100000,xp_required=20000),
        LevelTuple(level=16,total_xp=120000,xp_required=20000),
        LevelTuple(level=17,total_xp=140000,xp_required=20000),
        LevelTuple(level=18,total_xp=160000,xp_required=25000),
        LevelTuple(level=19,total_xp=185000,xp_required=25000),
        LevelTuple(level=20,total_xp=210000,xp_required=50000),
        LevelTuple(level=21,total_xp=260000,xp_required=75000),
        LevelTuple(level=22,total_xp=335000,xp_required=100000),
        LevelTuple(level=23,total_xp=435000,xp_required=125000),
        LevelTuple(level=24,total_xp=560000,xp_required=150000),
        LevelTuple(level=25,total_xp=710000,xp_required=190000),
        LevelTuple(level=26,total_xp=900000,xp_required=200000),
        LevelTuple(level=27,total_xp=1100000,xp_required=250000),
        LevelTuple(level=28,total_xp=1350000,xp_required=300000),
        LevelTuple(level=29,total_xp=1650000,xp_required=350000),
        LevelTuple(level=30,total_xp=2000000,xp_required=500000),
        LevelTuple(level=31,total_xp=2500000,xp_required=500000),
        LevelTuple(level=32,total_xp=3000000,xp_required=750000),
        LevelTuple(level=33,total_xp=3750000,xp_required=1000000),
        LevelTuple(level=34,total_xp=4750000,xp_required=1250000),
        LevelTuple(level=35,total_xp=6000000,xp_required=1500000),
        LevelTuple(level=36,total_xp=7500000,xp_required=2000000),
        LevelTuple(level=37,total_xp=9500000,xp_required=2500000),
        LevelTuple(level=38,total_xp=12000000,xp_required=3000000),
        LevelTuple(level=39,total_xp=15000000,xp_required=5000000),
        LevelTuple(level=40,total_xp=20000000,xp_required=float("inf"))
        ]
    
    if xp and level:
        raise ValueError
    if xp is not None:
        for level in LevelTuples:
            if level.total_xp <= xp < (level.total_xp+level.xp_required):
                return level
    if level:
        return next((x for x in LevelTuples if x.level == level), None)
    else:
        raise ValueError

UPDATE_FIELDS_BADGES = (
    'travel_km',
    'capture_total',
    'evolved_total',
    'hatched_total',
    'pokestops_visited',
    'big_magikarp',
    'battle_attack_won',
    'battle_training_won',
    'small_rattata',
    'pikachu',
    'unown',
    'raid_battle_won',
    'legendary_battle_won',
    'berries_fed',
    'hours_defended',
    'challenge_quests',
    'max_level_friends',
    'trading',
    'trading_distance',
    'great_league',
    'ultra_league',
    'master_league',
    'photobomb',
    'pokemon_purified',
    'photobombadge_rocket_grunts_defeat',
    )

UPDATE_FIELDS_TYPES = (
    'type_normal',
    'type_fighting',
    'type_flying',
    'type_poison',
    'type_ground',
    'type_rock',
    'type_bug',
    'type_ghost',
    'type_steel',
    'type_fire',
    'type_water',
    'type_grass',
    'type_electric',
    'type_psychic',
    'type_ice',
    'type_dragon',
    'type_dark',
    'type_fairy',
)

UPDATE_FIELDS_POKEDEX = (
    'pokedex_total_caught',
    'pokedex_total_seen',
    'pokedex_gen1',
    'pokedex_gen2',
    'pokedex_gen3',
    'pokedex_gen4',
    'pokedex_gen5',
    'pokedex_gen6',
    'pokedex_gen7',
    'pokedex_gen8',
)

UPDATE_SORTABLE_FIELDS = (
    'total_xp',
    'gymbadges_total',
    'gymbadges_gold',
) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES

UPDATE_NON_REVERSEABLE_FIELDS = ('total_xp', 'gymbadges_total', 'gymbadges_gold',) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + UPDATE_FIELDS_POKEDEX

BADGES = [
    {'name':'badge_travel_km', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_pokedex_entries', 'bronze':5, 'silver':50, 'gold':100},
    {'name':'badge_capture_total', 'bronze':30, 'silver':500, 'gold':2000},
    {'name':'badge_evolved_total', 'bronze':3, 'silver':20, 'gold':200},
    {'name':'badge_hatched_total', 'bronze':10, 'silver':100, 'gold':500},
    {'name':'badge_pokestops_visited', 'bronze':100, 'silver':1000, 'gold':2000},
    {'name':'badge_big_magikarp', 'bronze':3, 'silver':50, 'gold':300},
    {'name':'badge_battle_attack_won', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_battle_training_won', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_small_rattata', 'bronze':3, 'silver':50, 'gold':300},
    {'name':'badge_pikachu', 'bronze':3, 'silver':50, 'gold':300},
    {'name':'badge_unown', 'bronze':5, 'silver':30, 'gold':70},
    {'name':'badge_pokedex_entries_gen2', 'bronze':3, 'silver':10, 'gold':26},
    {'name':'badge_raid_battle_won', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_legendary_battle_won', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_berries_fed', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_hours_defended', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_pokedex_entries_gen3', 'bronze':5, 'silver':40, 'gold':90},
    {'name':'badge_challenge_quests', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_max_level_friends', 'bronze':1, 'silver':2, 'gold':3},
    {'name':'badge_trading', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_trading_distance', 'bronze':1000, 'silver':10000, 'gold':1000000},
    {'name':'badge_pokedex_entries_gen4', 'bronze':5, 'silver':30, 'gold':80},
    {'name':'badge_great_league', 'bronze':5, 'silver':50, 'gold':200},
    {'name':'badge_ultra_league', 'bronze':5, 'silver':50, 'gold':200},
    {'name':'badge_master_league', 'bronze':5, 'silver':50, 'gold':200},
    {'name':'badge_photobomb', 'bronze': 10, 'silver': 50, 'gold':200},
    {'name':'badge_pokedex_entries_gen5', 'bronze':5, 'silver':50, 'gold':100},
    {'name':'badge_pokemon_purified', 'bronze':5, 'silver':50, 'gold':500},
    {'name':'badge_photobombadge_rocket_grunts_defeated', 'bronze':10, 'silver':100, 'gold':1000},
    {'name':'badge_pokedex_entries_gen8', 'bronze': 1, 'silver': 1, 'gold':2},
] +  [{'name':x, 'bronze':10, 'silver':50, 'gold':200} for x in UPDATE_FIELDS_TYPES]

def circled_level(i: int):
    
    numbers = [9312,9313,9314,9315,9316,9317,9318,9319,9320,9321,9322,9323,9324,9325,9326,9327,9328,9329,9330,9331,12881,12882,12883,12884,12885,12886,12887,12888,12889,12890,12891,12892,12893,12894,12895,12977,12978,12979,12980,12981,12982,12983,12984,12985,12986,12987,12988,12989,12990,12991]
    
    if i <= 0:
        return ""
    try:
        return chr(numbers[i-1])
    except IndexError:
        return ""

def chunks(l,n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
