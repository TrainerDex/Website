// Service / Factory
var MOVES = {
    1: 'Thunder Shock',
    2: 'Quick Attack',
    3: 'Scratch',
    4: 'Ember',
    5: 'Vine Whip',
    6: 'Tackle',
    7: 'Razor Leaf',
    8: 'Take Down',
    9: 'Water Gun',
    10: 'Bite',
    11: 'Pound',
    12: 'Double Slap',
    13: 'Wrap',
    14: 'Hyper Beam',
    15: 'Lick',
    16: 'Dark Pulse',
    17: 'Smog',
    18: 'Sludge',
    19: 'Metal Claw',
    20: 'Vice Grip',
    21: 'Flame Wheel',
    22: 'Megahorn',
    23: 'Wing Attack',
    24: 'Flamethrower',
    25: 'Sucker Punch',
    26: 'Dig',
    27: 'Low Kick',
    28: 'Cross Chop',
    29: 'Psycho Cut',
    30: 'Psybeam',
    31: 'Earthquake',
    32: 'Stone Edge',
    33: 'Ice Punch',
    34: 'Heart Stamp',
    35: 'Discharge',
    36: 'Flash Cannon',
    37: 'Peck',
    38: 'Drill Peck',
    39: 'Ice Beam',
    40: 'Blizzard',
    41: 'Air Slash',
    42: 'Heat Wave',
    43: 'Twineedle',
    44: 'Poison Jab',
    45: 'Aerial Ace',
    46: 'Drill Run',
    47: 'Petal Blizzard',
    48: 'Mega Drain',
    49: 'Bug Buzz',
    50: 'Poison Fang',
    51: 'Night Slash',
    52: 'Slash',
    53: 'Bubble Beam',
    54: 'Submission',
    55: 'Karate Chop',
    56: 'Low Sweep',
    57: 'Aqua Jet',
    58: 'Aqua Tail',
    59: 'Seed Bomb',
    60: 'Psyshock',
    61: 'Rock Throw',
    62: 'Ancient Power',
    63: 'Rock Tomb',
    64: 'Rock Slide',
    65: 'Power Gem',
    66: 'Shadow Sneak',
    67: 'Shadow Punch',
    68: 'Shadow Claw',
    69: 'Ominous Wind',
    70: 'Shadow Ball',
    71: 'Bullet Punch',
    72: 'Magnet Bomb',
    73: 'Steel Wing',
    74: 'Iron Head',
    75: 'Parabolic Charge',
    76: 'Spark',
    77: 'Thunder Punch',
    78: 'Thunder',
    79: 'Thunderbolt',
    80: 'Twister',
    81: 'Dragon Breath',
    82: 'Dragon Pulse',
    83: 'Dragon Claw',
    84: 'Disarming Voice',
    85: 'Draining Kiss',
    86: 'Dazzling Gleam',
    87: 'Moonblast',
    88: 'Play Rough',
    89: 'Cross Poison',
    90: 'Sludge Bomb',
    91: 'Sludge Wave',
    92: 'Gunk Shot',
    93: 'Mud Shot',
    94: 'Bone Club',
    95: 'Bulldoze',
    96: 'Mud Bomb',
    97: 'Fury Cutter',
    98: 'Bug Bite',
    99: 'Signal Beam',
    100: 'X-Scissor',
    101: 'Flame Charge',
    102: 'Flame Burst',
    103: 'Fire Blast',
    104: 'Brine',
    105: 'Water Pulse',
    106: 'Scald',
    107: 'Hydro Pump',
    108: 'Psychic',
    109: 'Psystrike',
    110: 'Ice Shard',
    111: 'Icy Wind',
    112: 'Frost Breath',
    113: 'Absorb',
    114: 'Giga Drain',
    115: 'Fire Punch',
    116: 'Solar Beam',
    117: 'Leaf Blade',
    118: 'Power Whip',
    119: 'Splash',
    120: 'Acid',
    121: 'Air Cutter',
    122: 'Hurricane',
    123: 'Brick Break',
    124: 'Cut',
    125: 'Swift',
    126: 'Horn Attack',
    127: 'Stomp',
    128: 'Headbutt',
    129: 'Hyper Fang',
    130: 'Slam',
    131: 'Body Slam',
    132: 'Rest',
    133: 'Struggle',
    134: 'Scald',
    135: 'Hydro Pump',
    136: 'Wrap',
    137: 'Wrap',
    200: 'Fury Cutter',
    201: 'Bug Bite',
    202: 'Bite',
    203: 'Sucker Punch',
    204: 'Dragon Breath',
    205: 'Thunder Shock',
    206: 'Spark',
    207: 'Low Kick',
    208: 'Karate Chop',
    209: 'Ember',
    210: 'Wing Attack',
    211: 'Peck',
    212: 'Lick',
    213: 'Shadow Claw',
    214: 'Vine Whip',
    215: 'Razor Leaf',
    216: 'Mud Shot',
    217: 'Ice Shard',
    218: 'Frost Breath',
    219: 'Quick Attack',
    220: 'Scratch',
    221: 'Tackle',
    222: 'Pound',
    223: 'Cut',
    224: 'Poison Jab',
    225: 'Acid',
    226: 'Psycho Cut',
    227: 'Rock Throw',
    228: 'Metal Claw',
    229: 'Bullet Punch',
    230: 'Water Gun',
    231: 'Splash',
    232: 'Water Gun',
    233: 'Mud Slap',
    234: 'Zen Headbutt',
    235: 'Confusion',
    236: 'Poison Sting',
    237: 'Bubble',
    238: 'Feint Attack',
    239: 'Steel Wing',
    240: 'Fire Fang',
    241: 'Rock Smash',
    242: 'Transform',
    243: 'Counter',
    244: 'Powder Snow',
    245: 'Close Combat',
    246: 'Dynamic Punch',
    247: 'Focus Blast',
    248: 'Aurora Beam',
    249: 'Charge Beam',
    250: 'Volt Switch',
    251: 'Wild Charge',
    252: 'Zap Cannon',
    253: 'Dragon Tail',
    254: 'Avalanche',
    255: 'Air Slash',
    256: 'Brave Bird',
    257: 'Sky Attack',
    258: 'Sand Tomb',
    259: 'Rock Blast',
    260: 'Infestation',
    261: 'Struggle Bug',
    262: 'Silver Wind',
    263: 'Astonish',
    264: 'Hex',
    265: 'Night Shade',
    266: 'Iron Tail',
    267: 'Gyro Ball',
    268: 'Heavy Slam',
    269: 'Fire Spin',
    270: 'Overheat',
    271: 'Bullet Seed',
    272: 'Grass Knot',
    273: 'Energy Ball',
    274: 'Extrasensory',
    275: 'Future Sight',
    276: 'Mirror Coat',
    277: 'Outrage',
    278: 'Snarl',
    279: 'Crunch',
    280: 'Foul Play',
    281: 'Hidden Power'
}

angular.module("ekpogo").factory("GymData", GymDataService);
function GymDataService($http, $q) {
  return {
    fetch: fetch,
    getNext: getNext
  };

  function parse_results(results) {
    var now = new Date;
    for (i = 0; i < results.length; i++) {
      if (results[i].raid_start) {
        console.log(results[i].raid_start);
        results[i].raid_start = new Date(Date.parse(results[i].raid_start));
        results[i].raid_end = new Date(Date.parse(results[i].raid_end));
        results[i].move_1_name = MOVES[results[i].raid_pokemon_move_1];
        results[i].move_2_name = MOVES[results[i].raid_pokemon_move_2];
        console.log(results[i].raid_start);
      }
    }
    return results;
  }
  
  function fetch() {
    var deferred = $q.defer();
    
    $http.get("/api/0.1/gyms/?raid_active=true")
      .then(function(results) {
        if (results.data) {
          next = results.data.next || null;
          previous = results.data.previous || null;
          deferred.resolve(parse_results(results.data.results));
        }
    }, function(error) {
      deferred.reject(error);
    });
    
    return deferred.promise;
  }

  function getNext() {
    var deferred = $q.defer();
    
    if (next) {
      $http.get(next)
        .then(function(results) {
          if (results.data) {
            next = results.data.next || null;
            previous = results.data.previous || null;
            deferred.resolve(parse_results(results.data.results));
          }
        }, function(error) {
          deferred.reject(error);
        });
    } else {
      deferred.reject();
    }
    return deferred.promise;
  }
}
