import json

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

def level_parser(xp: int=None, level: int=None):
    """
    Takes either xp OR level and returns the value for the other
    """
    
    assert not all((xp, level))
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_fields_metadata.json'), 'r') as file:
        _levels = json.load(file).get('total_xp').get('levels')
    
    if level and 1<=level<=40:
        _levels.get(str(level))
    
    if xp:
        # Check if on final level
        final_level = list(_levels.items())[-1]
        if xp >= final_level[1]:
            return int(final_level[0])
        else:
            # Loop over levels, if the minimum requirement of that level is lower than the value provided, this is the first level the user hasn't accomplished. Go back one and it should be the right answer
            for k,v in _levels.items():
                if v > xp:
                    return int(k)-1

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
