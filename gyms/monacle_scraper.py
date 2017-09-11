import requests
import datetime
import time
from collections import namedtuple
from enum import Enum

class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    VERY_RARE = 4
    ULTRA_RARE = 5

class Team(Enum):
    MYSTIC=1
    VALOR=2
    INSTINCT=3

TEAM_NAMES = {
    0: 'Uncontested',
    1: 'Mystic',
    2: 'Valor',
    3: 'Instinct'
}

Spawn = namedtuple('Spawn', [
    'disappear_time',
    'encounter_id',
    'location',
    'pokemon',
])

Pokemon = namedtuple('Pokemon', [
    'individual_attack',
    'individual_defense',
    'individual_stamina',
    'move_1',
    'move_2',
    'weight',
    'height',
    'cp',
    'cp_multiplier',
    'level',
    'gender',
    'form',
    'id',
    'name',
    'rarity',
    'types',
])

Pokestop = namedtuple('Pokestop', [
    'active_fort_modifier',
    'enabled',
    'last_modified',
    'location',
    'lure_expiration',
    'id',
])

Gym = namedtuple('Gym', [
    'enabled',
    'guard_pokemon_id',
    'id',
    'slots_available',
    'last_modified',
    'location',
    'name',
    'team',
    'team_name',
    'pokemon',
    'total_gym_cp',
    'raid_level',
    'raid_pokemon',
    'raid_start',
    'raid_end',
])

def bts(b):
    '''
        Bool To String, the API wants 'true' and 'false' instead of normal bools
    '''
    return 'true' if b else 'false'

def stv(s):
    '''
        String to value, converts 'null', 'true', 'false' to their python counterparts
    '''
    return {'true': True, 'false': False, 'null': None}.get(s, s)

def string_to_rarity(s):
    '''
        Convert a string (eg "Common") into a Rarity
    '''
    return getattr(Rarity, s.upper().replace(' ', '_'))

class MonacleScraper(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.session = requests.Session()

    def get_raw_data(self, sw_point, ne_point, pokemon=True, pokestops=True, lured_only=False, gyms=True):
        """
            Get data from the Monacle server
            
            pokemon: If true, get data about pokemon spawns
            pokestops: If true, get data about pokestops
            lured_only: If pokestops is true and you set this to true, only return lured pokestops.
            gyms: If true, get data about gyms
            sw_point: South west corner of the box to search, (lat, long)
            ne_point: North east corner of the box to search, (lat, long)
        """

        data = {
            'timestamp': int(time.time()),
            'pokemon': bts(pokemon),
            'lastpokemon': 'true',
            'pokestops': bts(pokestops),
            'lastpokestops': 'true',
            'luredonly': bts(lured_only),
            'gyms': bts(gyms),
            'lastgyms': 'true',
            'scanned': 'false',
            'lastslocs': 'false',
            'spawnpoints': 'false',
            'lastspawns': 'false',
            'swLat': sw_point[0],
            'swLng': sw_point[1],
            'neLat': ne_point[0],
            'neLng': ne_point[1],
            'oSwLat': sw_point[0],
            'oSwLng': sw_point[1],
            'oNeLat': ne_point[0],
            'oNeLng': ne_point[1],
            'eids': '',
            'token': self.token
        }

        r = self.session.post(self.url, data=data)
        response = r.json()
        spawns = []
        
        # For some stupid reason, the server sometimes returns a dict, sometimes a list. Have to handle this.
        pokemons = response.get('pokemons', [])
        if isinstance(pokemons, dict):
            pokemons = pokemons.values()
        for spawn in pokemons:
            pokemon = Pokemon(
                individual_attack=stv(spawn['individual_attack']),
                individual_defense=stv(spawn['individual_defense']),
                individual_stamina=stv(spawn['individual_stamina']),
                move_1=stv(spawn['move_1']),
                move_2=stv(spawn['move_2']),
                weight=stv(spawn['weight']),
                height=stv(spawn['height']),
                cp=stv(spawn['cp']),
                cp_multiplier=stv(spawn['cp_multiplier']),
                level=stv(spawn['level']),
                gender=stv(spawn['gender']),
                form=stv(spawn['form']),
                id=spawn['pokemon_id'],
                name=spawn['pokemon_name'],
                rarity=string_to_rarity(spawn['pokemon_rarity']),
                types='', # TODO: Make this actually work
            )
            spawns.append(Spawn(
                disappear_time=datetime.datetime.fromtimestamp(spawn['disappear_time'] / 1000),
                encounter_id=int(spawn['encounter_id']),
                location=(spawn['latitude'], spawn['longitude']),
                pokemon=pokemon,
            ))                
        
        pokestops = []
        for pokestop in response.get('pokestops', []):
            pokestops.append(Pokestop(
                active_fort_modifier=stv(pokestop['active_fort_modifier']),
                enabled=stv(pokestop['enabled']),
                last_modified=None if pokestop['last_modified'] == 0 else datetime.datetime.fromtimestamp(pokestop['last_modified'] / 1000),
                location=(pokestop['latitude'], pokestop['longitude']),
                lure_expiration='', # TODO: Make this work, map may not be pulling this information
                id=pokestop['pokestop_id']
            ))

        gyms = []
        gyms_list = response.get('gyms', [])
        if isinstance(gyms_list, dict):
            gyms_list = gyms_list.values()
        for gym in gyms_list:
            if gym.get('raid_pokemon_id'):
                raid_pokemon = Pokemon(
                    id=int(gym['raid_pokemon_id']),
                    name=gym['raid_pokemon_name'],
                    cp=gym['raid_pokemon_cp'],
                    move_1=gym['raid_pokemon_move_1'],
                    move_2=gym['raid_pokemon_move_2'],
                    individual_attack=None,
                    individual_defense=None,
                    individual_stamina=None,
                    weight=None,
                    height=None,
                    cp_multiplier=None,
                    level=None,
                    gender=None,
                    form=None,
                    rarity=None,
                    types=None
                )
                raid_start = datetime.datetime.fromtimestamp(gym['raid_start'] / 1000)
                raid_end = datetime.datetime.fromtimestamp(gym['raid_end'] / 1000)
            else:
                raid_pokemon = None
                raid_start = None
                raid_end = None

            gyms.append(Gym(
                enabled=stv(gym['enabled']),
                guard_pokemon_id=gym['guard_pokemon_id'],
                id=gym['gym_id'],
                slots_available=int(gym['slots_available']),
                last_modified=None if gym['last_modified'] == 0 else datetime.datetime.fromtimestamp(gym['last_modified'] / 1000),
                location=(gym['latitude'], gym['longitude']),
                name=None, # KentPogoMap doesn't enter gyms for scanning currently
                team=int(gym['team_id']),
                team_name=TEAM_NAMES[int(gym['team_id'])],
                pokemon=[], # KentPogoMap doesn't enter gyms for scanning currently
                total_gym_cp=None,
                raid_level=int(gym.get('raid_level')),
                raid_pokemon=raid_pokemon,
                raid_start=raid_start,
                raid_end=raid_end
            ))
        return spawns, pokestops, gyms
