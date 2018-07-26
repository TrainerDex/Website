# -*- coding: utf-8 -*-
from collections import namedtuple
from distutils.util import strtobool

def strtoboolornone(value):
	try:
		return bool(strtobool(value))
	except (ValueError, AttributeError):
		return None

def cleanleaderboardqueryset(queryset, **kwargs):
	value = list(queryset)
	for x in value:
		if x.update__xp__max is None or x.update__xp__max is 0:
			value.remove(x)
	return sorted(value, **kwargs)

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
	'walk_dist',
	'gen_1_dex',
	'pkmn_caught',
	'pkmn_evolved',
	'eggs_hatched',
	'pkstops_spun',
	'big_magikarp',
	'battles_won',
	'legacy_gym_trained',
	'tiny_rattata',
	'pikachu_caught',
	'gen_2_dex',
	'unown_alphabet',
	'berry_fed',
	'gym_defended',
	'raids_completed',
	'leg_raids_completed',
	'gen_3_dex',
	'quests',
	'max_friends',
	'trading',
	'trading_distance',
)

UPDATE_FIELDS_TYPES = (
	'pkmn_normal',
	'pkmn_fighting',
	'pkmn_flying',
	'pkmn_poison',
	'pkmn_ground',
	'pkmn_rock',
	'pkmn_bug',
	'pkmn_ghost',
	'pkmn_steel',
	'pkmn_fire',
	'pkmn_water',
	'pkmn_grass',
	'pkmn_electric',
	'pkmn_psychic',
	'pkmn_ice',
	'pkmn_dragon',
	'pkmn_dark',
	'pkmn_fairy',
)

UPDATE_SORTABLE_FIELDS = (
	'xp',
	'dex_caught',
	'dex_seen',
	'gym_badges',
) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES

numbers = [9312,9313,9314,9315,9316,9317,9318,9319,9320,9321,9322,9323,9324,9325,9326,9327,9328,9329,9330,9331,12881,12882,12883,12884,12885,12886,12887,12888,12889,12890,12891,12892,12893,12894,12895,12977,12978,12979,12980,12981,12982,12983,12984,12985,12986,12987,12988,12989,12990,12991]

def int_to_unicode(i):
	if i <= 0:
		return ""
	try:
		return chr(numbers[i-1])
	except IndexError:
		return ""

flags = [
	{
		"code": "AD",
		"emoji": "🇦🇩",
		"unicode": "U+1F1E6 U+1F1E9",
		"name": "Andorra",
		"title": "flag for Andorra"
	},
	{
		"code": "AE",
		"emoji": "🇦🇪",
		"unicode": "U+1F1E6 U+1F1EA",
		"name": "United Arab Emirates",
		"title": "flag for United Arab Emirates"
	},
	{
		"code": "AF",
		"emoji": "🇦🇫",
		"unicode": "U+1F1E6 U+1F1EB",
		"name": "Afghanistan",
		"title": "flag for Afghanistan"
	},
	{
		"code": "AG",
		"emoji": "🇦🇬",
		"unicode": "U+1F1E6 U+1F1EC",
		"name": "Antigua and Barbuda",
		"title": "flag for Antigua and Barbuda"
	},
	{
		"code": "AI",
		"emoji": "🇦🇮",
		"unicode": "U+1F1E6 U+1F1EE",
		"name": "Anguilla",
		"title": "flag for Anguilla"
	},
	{
		"code": "AL",
		"emoji": "🇦🇱",
		"unicode": "U+1F1E6 U+1F1F1",
		"name": "Albania",
		"title": "flag for Albania"
	},
	{
		"code": "AM",
		"emoji": "🇦🇲",
		"unicode": "U+1F1E6 U+1F1F2",
		"name": "Armenia",
		"title": "flag for Armenia"
	},
	{
		"code": "AO",
		"emoji": "🇦🇴",
		"unicode": "U+1F1E6 U+1F1F4",
		"name": "Angola",
		"title": "flag for Angola"
	},
	{
		"code": "AQ",
		"emoji": "🇦🇶",
		"unicode": "U+1F1E6 U+1F1F6",
		"name": "Antarctica",
		"title": "flag for Antarctica"
	},
	{
		"code": "AR",
		"emoji": "🇦🇷",
		"unicode": "U+1F1E6 U+1F1F7",
		"name": "Argentina",
		"title": "flag for Argentina"
	},
	{
		"code": "AS",
		"emoji": "🇦🇸",
		"unicode": "U+1F1E6 U+1F1F8",
		"name": "American Samoa",
		"title": "flag for American Samoa"
	},
	{
		"code": "AT",
		"emoji": "🇦🇹",
		"unicode": "U+1F1E6 U+1F1F9",
		"name": "Austria",
		"title": "flag for Austria"
	},
	{
		"code": "AU",
		"emoji": "🇦🇺",
		"unicode": "U+1F1E6 U+1F1FA",
		"name": "Australia",
		"title": "flag for Australia"
	},
	{
		"code": "AW",
		"emoji": "🇦🇼",
		"unicode": "U+1F1E6 U+1F1FC",
		"name": "Aruba",
		"title": "flag for Aruba"
	},
	{
		"code": "AX",
		"emoji": "🇦🇽",
		"unicode": "U+1F1E6 U+1F1FD",
		"name": "Åland Islands",
		"title": "flag for Åland Islands"
	},
	{
		"code": "AZ",
		"emoji": "🇦🇿",
		"unicode": "U+1F1E6 U+1F1FF",
		"name": "Azerbaijan",
		"title": "flag for Azerbaijan"
	},
	{
		"code": "BA",
		"emoji": "🇧🇦",
		"unicode": "U+1F1E7 U+1F1E6",
		"name": "Bosnia and Herzegovina",
		"title": "flag for Bosnia and Herzegovina"
	},
	{
		"code": "BB",
		"emoji": "🇧🇧",
		"unicode": "U+1F1E7 U+1F1E7",
		"name": "Barbados",
		"title": "flag for Barbados"
	},
	{
		"code": "BD",
		"emoji": "🇧🇩",
		"unicode": "U+1F1E7 U+1F1E9",
		"name": "Bangladesh",
		"title": "flag for Bangladesh"
	},
	{
		"code": "BE",
		"emoji": "🇧🇪",
		"unicode": "U+1F1E7 U+1F1EA",
		"name": "Belgium",
		"title": "flag for Belgium"
	},
	{
		"code": "BF",
		"emoji": "🇧🇫",
		"unicode": "U+1F1E7 U+1F1EB",
		"name": "Burkina Faso",
		"title": "flag for Burkina Faso"
	},
	{
		"code": "BG",
		"emoji": "🇧🇬",
		"unicode": "U+1F1E7 U+1F1EC",
		"name": "Bulgaria",
		"title": "flag for Bulgaria"
	},
	{
		"code": "BH",
		"emoji": "🇧🇭",
		"unicode": "U+1F1E7 U+1F1ED",
		"name": "Bahrain",
		"title": "flag for Bahrain"
	},
	{
		"code": "BI",
		"emoji": "🇧🇮",
		"unicode": "U+1F1E7 U+1F1EE",
		"name": "Burundi",
		"title": "flag for Burundi"
	},
	{
		"code": "BJ",
		"emoji": "🇧🇯",
		"unicode": "U+1F1E7 U+1F1EF",
		"name": "Benin",
		"title": "flag for Benin"
	},
	{
		"code": "BL",
		"emoji": "🇧🇱",
		"unicode": "U+1F1E7 U+1F1F1",
		"name": "Saint Barthélemy",
		"title": "flag for Saint Barthélemy"
	},
	{
		"code": "BM",
		"emoji": "🇧🇲",
		"unicode": "U+1F1E7 U+1F1F2",
		"name": "Bermuda",
		"title": "flag for Bermuda"
	},
	{
		"code": "BN",
		"emoji": "🇧🇳",
		"unicode": "U+1F1E7 U+1F1F3",
		"name": "Brunei Darussalam",
		"title": "flag for Brunei Darussalam"
	},
	{
		"code": "BO",
		"emoji": "🇧🇴",
		"unicode": "U+1F1E7 U+1F1F4",
		"name": "Bolivia",
		"title": "flag for Bolivia"
	},
	{
		"code": "BQ",
		"emoji": "🇧🇶",
		"unicode": "U+1F1E7 U+1F1F6",
		"name": "Bonaire, Sint Eustatius and Saba",
		"title": "flag for Bonaire, Sint Eustatius and Saba"
	},
	{
		"code": "BR",
		"emoji": "🇧🇷",
		"unicode": "U+1F1E7 U+1F1F7",
		"name": "Brazil",
		"title": "flag for Brazil"
	},
	{
		"code": "BS",
		"emoji": "🇧🇸",
		"unicode": "U+1F1E7 U+1F1F8",
		"name": "Bahamas",
		"title": "flag for Bahamas"
	},
	{
		"code": "BT",
		"emoji": "🇧🇹",
		"unicode": "U+1F1E7 U+1F1F9",
		"name": "Bhutan",
		"title": "flag for Bhutan"
	},
	{
		"code": "BV",
		"emoji": "🇧🇻",
		"unicode": "U+1F1E7 U+1F1FB",
		"name": "Bouvet Island",
		"title": "flag for Bouvet Island"
	},
	{
		"code": "BW",
		"emoji": "🇧🇼",
		"unicode": "U+1F1E7 U+1F1FC",
		"name": "Botswana",
		"title": "flag for Botswana"
	},
	{
		"code": "BY",
		"emoji": "🇧🇾",
		"unicode": "U+1F1E7 U+1F1FE",
		"name": "Belarus",
		"title": "flag for Belarus"
	},
	{
		"code": "BZ",
		"emoji": "🇧🇿",
		"unicode": "U+1F1E7 U+1F1FF",
		"name": "Belize",
		"title": "flag for Belize"
	},
	{
		"code": "CA",
		"emoji": "🇨🇦",
		"unicode": "U+1F1E8 U+1F1E6",
		"name": "Canada",
		"title": "flag for Canada"
	},
	{
		"code": "CC",
		"emoji": "🇨🇨",
		"unicode": "U+1F1E8 U+1F1E8",
		"name": "Cocos (Keeling) Islands",
		"title": "flag for Cocos (Keeling) Islands"
	},
	{
		"code": "CD",
		"emoji": "🇨🇩",
		"unicode": "U+1F1E8 U+1F1E9",
		"name": "Congo",
		"title": "flag for Congo"
	},
	{
		"code": "CF",
		"emoji": "🇨🇫",
		"unicode": "U+1F1E8 U+1F1EB",
		"name": "Central African Republic",
		"title": "flag for Central African Republic"
	},
	{
		"code": "CG",
		"emoji": "🇨🇬",
		"unicode": "U+1F1E8 U+1F1EC",
		"name": "Congo",
		"title": "flag for Congo"
	},
	{
		"code": "CH",
		"emoji": "🇨🇭",
		"unicode": "U+1F1E8 U+1F1ED",
		"name": "Switzerland",
		"title": "flag for Switzerland"
	},
	{
		"code": "CI",
		"emoji": "🇨🇮",
		"unicode": "U+1F1E8 U+1F1EE",
		"name": "Côte D'Ivoire",
		"title": "flag for Côte D'Ivoire"
	},
	{
		"code": "CK",
		"emoji": "🇨🇰",
		"unicode": "U+1F1E8 U+1F1F0",
		"name": "Cook Islands",
		"title": "flag for Cook Islands"
	},
	{
		"code": "CL",
		"emoji": "🇨🇱",
		"unicode": "U+1F1E8 U+1F1F1",
		"name": "Chile",
		"title": "flag for Chile"
	},
	{
		"code": "CM",
		"emoji": "🇨🇲",
		"unicode": "U+1F1E8 U+1F1F2",
		"name": "Cameroon",
		"title": "flag for Cameroon"
	},
	{
		"code": "CN",
		"emoji": "🇨🇳",
		"unicode": "U+1F1E8 U+1F1F3",
		"name": "China",
		"title": "flag for China"
	},
	{
		"code": "CO",
		"emoji": "🇨🇴",
		"unicode": "U+1F1E8 U+1F1F4",
		"name": "Colombia",
		"title": "flag for Colombia"
	},
	{
		"code": "CR",
		"emoji": "🇨🇷",
		"unicode": "U+1F1E8 U+1F1F7",
		"name": "Costa Rica",
		"title": "flag for Costa Rica"
	},
	{
		"code": "CU",
		"emoji": "🇨🇺",
		"unicode": "U+1F1E8 U+1F1FA",
		"name": "Cuba",
		"title": "flag for Cuba"
	},
	{
		"code": "CV",
		"emoji": "🇨🇻",
		"unicode": "U+1F1E8 U+1F1FB",
		"name": "Cape Verde",
		"title": "flag for Cape Verde"
	},
	{
		"code": "CW",
		"emoji": "🇨🇼",
		"unicode": "U+1F1E8 U+1F1FC",
		"name": "Curaçao",
		"title": "flag for Curaçao"
	},
	{
		"code": "CX",
		"emoji": "🇨🇽",
		"unicode": "U+1F1E8 U+1F1FD",
		"name": "Christmas Island",
		"title": "flag for Christmas Island"
	},
	{
		"code": "CY",
		"emoji": "🇨🇾",
		"unicode": "U+1F1E8 U+1F1FE",
		"name": "Cyprus",
		"title": "flag for Cyprus"
	},
	{
		"code": "CZ",
		"emoji": "🇨🇿",
		"unicode": "U+1F1E8 U+1F1FF",
		"name": "Czech Republic",
		"title": "flag for Czech Republic"
	},
	{
		"code": "DE",
		"emoji": "🇩🇪",
		"unicode": "U+1F1E9 U+1F1EA",
		"name": "Germany",
		"title": "flag for Germany"
	},
	{
		"code": "DJ",
		"emoji": "🇩🇯",
		"unicode": "U+1F1E9 U+1F1EF",
		"name": "Djibouti",
		"title": "flag for Djibouti"
	},
	{
		"code": "DK",
		"emoji": "🇩🇰",
		"unicode": "U+1F1E9 U+1F1F0",
		"name": "Denmark",
		"title": "flag for Denmark"
	},
	{
		"code": "DM",
		"emoji": "🇩🇲",
		"unicode": "U+1F1E9 U+1F1F2",
		"name": "Dominica",
		"title": "flag for Dominica"
	},
	{
		"code": "DO",
		"emoji": "🇩🇴",
		"unicode": "U+1F1E9 U+1F1F4",
		"name": "Dominican Republic",
		"title": "flag for Dominican Republic"
	},
	{
		"code": "DZ",
		"emoji": "🇩🇿",
		"unicode": "U+1F1E9 U+1F1FF",
		"name": "Algeria",
		"title": "flag for Algeria"
	},
	{
		"code": "EC",
		"emoji": "🇪🇨",
		"unicode": "U+1F1EA U+1F1E8",
		"name": "Ecuador",
		"title": "flag for Ecuador"
	},
	{
		"code": "EE",
		"emoji": "🇪🇪",
		"unicode": "U+1F1EA U+1F1EA",
		"name": "Estonia",
		"title": "flag for Estonia"
	},
	{
		"code": "EG",
		"emoji": "🇪🇬",
		"unicode": "U+1F1EA U+1F1EC",
		"name": "Egypt",
		"title": "flag for Egypt"
	},
	{
		"code": "EH",
		"emoji": "🇪🇭",
		"unicode": "U+1F1EA U+1F1ED",
		"name": "Western Sahara",
		"title": "flag for Western Sahara"
	},
	{
		"code": "ER",
		"emoji": "🇪🇷",
		"unicode": "U+1F1EA U+1F1F7",
		"name": "Eritrea",
		"title": "flag for Eritrea"
	},
	{
		"code": "ES",
		"emoji": "🇪🇸",
		"unicode": "U+1F1EA U+1F1F8",
		"name": "Spain",
		"title": "flag for Spain"
	},
	{
		"code": "ET",
		"emoji": "🇪🇹",
		"unicode": "U+1F1EA U+1F1F9",
		"name": "Ethiopia",
		"title": "flag for Ethiopia"
	},
	{
		"code": "EU",
		"emoji": "🇪🇺",
		"unicode": "U+1F1EA U+1F1FA",
		"name": "European Union",
		"title": "flag for European Union"
	},
	{
		"code": "FI",
		"emoji": "🇫🇮",
		"unicode": "U+1F1EB U+1F1EE",
		"name": "Finland",
		"title": "flag for Finland"
	},
	{
		"code": "FJ",
		"emoji": "🇫🇯",
		"unicode": "U+1F1EB U+1F1EF",
		"name": "Fiji",
		"title": "flag for Fiji"
	},
	{
		"code": "FK",
		"emoji": "🇫🇰",
		"unicode": "U+1F1EB U+1F1F0",
		"name": "Falkland Islands (Malvinas)",
		"title": "flag for Falkland Islands (Malvinas)"
	},
	{
		"code": "FM",
		"emoji": "🇫🇲",
		"unicode": "U+1F1EB U+1F1F2",
		"name": "Micronesia",
		"title": "flag for Micronesia"
	},
	{
		"code": "FO",
		"emoji": "🇫🇴",
		"unicode": "U+1F1EB U+1F1F4",
		"name": "Faroe Islands",
		"title": "flag for Faroe Islands"
	},
	{
		"code": "FR",
		"emoji": "🇫🇷",
		"unicode": "U+1F1EB U+1F1F7",
		"name": "France",
		"title": "flag for France"
	},
	{
		"code": "GA",
		"emoji": "🇬🇦",
		"unicode": "U+1F1EC U+1F1E6",
		"name": "Gabon",
		"title": "flag for Gabon"
	},
	{
		"code": "GB",
		"emoji": "🇬🇧",
		"unicode": "U+1F1EC U+1F1E7",
		"name": "United Kingdom",
		"title": "flag for United Kingdom"
	},
	{
		"code": "GD",
		"emoji": "🇬🇩",
		"unicode": "U+1F1EC U+1F1E9",
		"name": "Grenada",
		"title": "flag for Grenada"
	},
	{
		"code": "GE",
		"emoji": "🇬🇪",
		"unicode": "U+1F1EC U+1F1EA",
		"name": "Georgia",
		"title": "flag for Georgia"
	},
	{
		"code": "GF",
		"emoji": "🇬🇫",
		"unicode": "U+1F1EC U+1F1EB",
		"name": "French Guiana",
		"title": "flag for French Guiana"
	},
	{
		"code": "GG",
		"emoji": "🇬🇬",
		"unicode": "U+1F1EC U+1F1EC",
		"name": "Guernsey",
		"title": "flag for Guernsey"
	},
	{
		"code": "GH",
		"emoji": "🇬🇭",
		"unicode": "U+1F1EC U+1F1ED",
		"name": "Ghana",
		"title": "flag for Ghana"
	},
	{
		"code": "GI",
		"emoji": "🇬🇮",
		"unicode": "U+1F1EC U+1F1EE",
		"name": "Gibraltar",
		"title": "flag for Gibraltar"
	},
	{
		"code": "GL",
		"emoji": "🇬🇱",
		"unicode": "U+1F1EC U+1F1F1",
		"name": "Greenland",
		"title": "flag for Greenland"
	},
	{
		"code": "GM",
		"emoji": "🇬🇲",
		"unicode": "U+1F1EC U+1F1F2",
		"name": "Gambia",
		"title": "flag for Gambia"
	},
	{
		"code": "GN",
		"emoji": "🇬🇳",
		"unicode": "U+1F1EC U+1F1F3",
		"name": "Guinea",
		"title": "flag for Guinea"
	},
	{
		"code": "GP",
		"emoji": "🇬🇵",
		"unicode": "U+1F1EC U+1F1F5",
		"name": "Guadeloupe",
		"title": "flag for Guadeloupe"
	},
	{
		"code": "GQ",
		"emoji": "🇬🇶",
		"unicode": "U+1F1EC U+1F1F6",
		"name": "Equatorial Guinea",
		"title": "flag for Equatorial Guinea"
	},
	{
		"code": "GR",
		"emoji": "🇬🇷",
		"unicode": "U+1F1EC U+1F1F7",
		"name": "Greece",
		"title": "flag for Greece"
	},
	{
		"code": "GS",
		"emoji": "🇬🇸",
		"unicode": "U+1F1EC U+1F1F8",
		"name": "South Georgia",
		"title": "flag for South Georgia"
	},
	{
		"code": "GT",
		"emoji": "🇬🇹",
		"unicode": "U+1F1EC U+1F1F9",
		"name": "Guatemala",
		"title": "flag for Guatemala"
	},
	{
		"code": "GU",
		"emoji": "🇬🇺",
		"unicode": "U+1F1EC U+1F1FA",
		"name": "Guam",
		"title": "flag for Guam"
	},
	{
		"code": "GW",
		"emoji": "🇬🇼",
		"unicode": "U+1F1EC U+1F1FC",
		"name": "Guinea-Bissau",
		"title": "flag for Guinea-Bissau"
	},
	{
		"code": "GY",
		"emoji": "🇬🇾",
		"unicode": "U+1F1EC U+1F1FE",
		"name": "Guyana",
		"title": "flag for Guyana"
	},
	{
		"code": "HK",
		"emoji": "🇭🇰",
		"unicode": "U+1F1ED U+1F1F0",
		"name": "Hong Kong",
		"title": "flag for Hong Kong"
	},
	{
		"code": "HM",
		"emoji": "🇭🇲",
		"unicode": "U+1F1ED U+1F1F2",
		"name": "Heard Island and Mcdonald Islands",
		"title": "flag for Heard Island and Mcdonald Islands"
	},
	{
		"code": "HN",
		"emoji": "🇭🇳",
		"unicode": "U+1F1ED U+1F1F3",
		"name": "Honduras",
		"title": "flag for Honduras"
	},
	{
		"code": "HR",
		"emoji": "🇭🇷",
		"unicode": "U+1F1ED U+1F1F7",
		"name": "Croatia",
		"title": "flag for Croatia"
	},
	{
		"code": "HT",
		"emoji": "🇭🇹",
		"unicode": "U+1F1ED U+1F1F9",
		"name": "Haiti",
		"title": "flag for Haiti"
	},
	{
		"code": "HU",
		"emoji": "🇭🇺",
		"unicode": "U+1F1ED U+1F1FA",
		"name": "Hungary",
		"title": "flag for Hungary"
	},
	{
		"code": "ID",
		"emoji": "🇮🇩",
		"unicode": "U+1F1EE U+1F1E9",
		"name": "Indonesia",
		"title": "flag for Indonesia"
	},
	{
		"code": "IE",
		"emoji": "🇮🇪",
		"unicode": "U+1F1EE U+1F1EA",
		"name": "Ireland",
		"title": "flag for Ireland"
	},
	{
		"code": "IL",
		"emoji": "🇮🇱",
		"unicode": "U+1F1EE U+1F1F1",
		"name": "Israel",
		"title": "flag for Israel"
	},
	{
		"code": "IM",
		"emoji": "🇮🇲",
		"unicode": "U+1F1EE U+1F1F2",
		"name": "Isle of Man",
		"title": "flag for Isle of Man"
	},
	{
		"code": "IN",
		"emoji": "🇮🇳",
		"unicode": "U+1F1EE U+1F1F3",
		"name": "India",
		"title": "flag for India"
	},
	{
		"code": "IO",
		"emoji": "🇮🇴",
		"unicode": "U+1F1EE U+1F1F4",
		"name": "British Indian Ocean Territory",
		"title": "flag for British Indian Ocean Territory"
	},
	{
		"code": "IQ",
		"emoji": "🇮🇶",
		"unicode": "U+1F1EE U+1F1F6",
		"name": "Iraq",
		"title": "flag for Iraq"
	},
	{
		"code": "IR",
		"emoji": "🇮🇷",
		"unicode": "U+1F1EE U+1F1F7",
		"name": "Iran",
		"title": "flag for Iran"
	},
	{
		"code": "IS",
		"emoji": "🇮🇸",
		"unicode": "U+1F1EE U+1F1F8",
		"name": "Iceland",
		"title": "flag for Iceland"
	},
	{
		"code": "IT",
		"emoji": "🇮🇹",
		"unicode": "U+1F1EE U+1F1F9",
		"name": "Italy",
		"title": "flag for Italy"
	},
	{
		"code": "JE",
		"emoji": "🇯🇪",
		"unicode": "U+1F1EF U+1F1EA",
		"name": "Jersey",
		"title": "flag for Jersey"
	},
	{
		"code": "JM",
		"emoji": "🇯🇲",
		"unicode": "U+1F1EF U+1F1F2",
		"name": "Jamaica",
		"title": "flag for Jamaica"
	},
	{
		"code": "JO",
		"emoji": "🇯🇴",
		"unicode": "U+1F1EF U+1F1F4",
		"name": "Jordan",
		"title": "flag for Jordan"
	},
	{
		"code": "JP",
		"emoji": "🇯🇵",
		"unicode": "U+1F1EF U+1F1F5",
		"name": "Japan",
		"title": "flag for Japan"
	},
	{
		"code": "KE",
		"emoji": "🇰🇪",
		"unicode": "U+1F1F0 U+1F1EA",
		"name": "Kenya",
		"title": "flag for Kenya"
	},
	{
		"code": "KG",
		"emoji": "🇰🇬",
		"unicode": "U+1F1F0 U+1F1EC",
		"name": "Kyrgyzstan",
		"title": "flag for Kyrgyzstan"
	},
	{
		"code": "KH",
		"emoji": "🇰🇭",
		"unicode": "U+1F1F0 U+1F1ED",
		"name": "Cambodia",
		"title": "flag for Cambodia"
	},
	{
		"code": "KI",
		"emoji": "🇰🇮",
		"unicode": "U+1F1F0 U+1F1EE",
		"name": "Kiribati",
		"title": "flag for Kiribati"
	},
	{
		"code": "KM",
		"emoji": "🇰🇲",
		"unicode": "U+1F1F0 U+1F1F2",
		"name": "Comoros",
		"title": "flag for Comoros"
	},
	{
		"code": "KN",
		"emoji": "🇰🇳",
		"unicode": "U+1F1F0 U+1F1F3",
		"name": "Saint Kitts and Nevis",
		"title": "flag for Saint Kitts and Nevis"
	},
	{
		"code": "KP",
		"emoji": "🇰🇵",
		"unicode": "U+1F1F0 U+1F1F5",
		"name": "North Korea",
		"title": "flag for North Korea"
	},
	{
		"code": "KR",
		"emoji": "🇰🇷",
		"unicode": "U+1F1F0 U+1F1F7",
		"name": "South Korea",
		"title": "flag for South Korea"
	},
	{
		"code": "KW",
		"emoji": "🇰🇼",
		"unicode": "U+1F1F0 U+1F1FC",
		"name": "Kuwait",
		"title": "flag for Kuwait"
	},
	{
		"code": "KY",
		"emoji": "🇰🇾",
		"unicode": "U+1F1F0 U+1F1FE",
		"name": "Cayman Islands",
		"title": "flag for Cayman Islands"
	},
	{
		"code": "KZ",
		"emoji": "🇰🇿",
		"unicode": "U+1F1F0 U+1F1FF",
		"name": "Kazakhstan",
		"title": "flag for Kazakhstan"
	},
	{
		"code": "LA",
		"emoji": "🇱🇦",
		"unicode": "U+1F1F1 U+1F1E6",
		"name": "Lao People's Democratic Republic",
		"title": "flag for Lao People's Democratic Republic"
	},
	{
		"code": "LB",
		"emoji": "🇱🇧",
		"unicode": "U+1F1F1 U+1F1E7",
		"name": "Lebanon",
		"title": "flag for Lebanon"
	},
	{
		"code": "LC",
		"emoji": "🇱🇨",
		"unicode": "U+1F1F1 U+1F1E8",
		"name": "Saint Lucia",
		"title": "flag for Saint Lucia"
	},
	{
		"code": "LI",
		"emoji": "🇱🇮",
		"unicode": "U+1F1F1 U+1F1EE",
		"name": "Liechtenstein",
		"title": "flag for Liechtenstein"
	},
	{
		"code": "LK",
		"emoji": "🇱🇰",
		"unicode": "U+1F1F1 U+1F1F0",
		"name": "Sri Lanka",
		"title": "flag for Sri Lanka"
	},
	{
		"code": "LR",
		"emoji": "🇱🇷",
		"unicode": "U+1F1F1 U+1F1F7",
		"name": "Liberia",
		"title": "flag for Liberia"
	},
	{
		"code": "LS",
		"emoji": "🇱🇸",
		"unicode": "U+1F1F1 U+1F1F8",
		"name": "Lesotho",
		"title": "flag for Lesotho"
	},
	{
		"code": "LT",
		"emoji": "🇱🇹",
		"unicode": "U+1F1F1 U+1F1F9",
		"name": "Lithuania",
		"title": "flag for Lithuania"
	},
	{
		"code": "LU",
		"emoji": "🇱🇺",
		"unicode": "U+1F1F1 U+1F1FA",
		"name": "Luxembourg",
		"title": "flag for Luxembourg"
	},
	{
		"code": "LV",
		"emoji": "🇱🇻",
		"unicode": "U+1F1F1 U+1F1FB",
		"name": "Latvia",
		"title": "flag for Latvia"
	},
	{
		"code": "LY",
		"emoji": "🇱🇾",
		"unicode": "U+1F1F1 U+1F1FE",
		"name": "Libya",
		"title": "flag for Libya"
	},
	{
		"code": "MA",
		"emoji": "🇲🇦",
		"unicode": "U+1F1F2 U+1F1E6",
		"name": "Morocco",
		"title": "flag for Morocco"
	},
	{
		"code": "MC",
		"emoji": "🇲🇨",
		"unicode": "U+1F1F2 U+1F1E8",
		"name": "Monaco",
		"title": "flag for Monaco"
	},
	{
		"code": "MD",
		"emoji": "🇲🇩",
		"unicode": "U+1F1F2 U+1F1E9",
		"name": "Moldova",
		"title": "flag for Moldova"
	},
	{
		"code": "ME",
		"emoji": "🇲🇪",
		"unicode": "U+1F1F2 U+1F1EA",
		"name": "Montenegro",
		"title": "flag for Montenegro"
	},
	{
		"code": "MF",
		"emoji": "🇲🇫",
		"unicode": "U+1F1F2 U+1F1EB",
		"name": "Saint Martin (French Part)",
		"title": "flag for Saint Martin (French Part)"
	},
	{
		"code": "MG",
		"emoji": "🇲🇬",
		"unicode": "U+1F1F2 U+1F1EC",
		"name": "Madagascar",
		"title": "flag for Madagascar"
	},
	{
		"code": "MH",
		"emoji": "🇲🇭",
		"unicode": "U+1F1F2 U+1F1ED",
		"name": "Marshall Islands",
		"title": "flag for Marshall Islands"
	},
	{
		"code": "MK",
		"emoji": "🇲🇰",
		"unicode": "U+1F1F2 U+1F1F0",
		"name": "Macedonia",
		"title": "flag for Macedonia"
	},
	{
		"code": "ML",
		"emoji": "🇲🇱",
		"unicode": "U+1F1F2 U+1F1F1",
		"name": "Mali",
		"title": "flag for Mali"
	},
	{
		"code": "MM",
		"emoji": "🇲🇲",
		"unicode": "U+1F1F2 U+1F1F2",
		"name": "Myanmar",
		"title": "flag for Myanmar"
	},
	{
		"code": "MN",
		"emoji": "🇲🇳",
		"unicode": "U+1F1F2 U+1F1F3",
		"name": "Mongolia",
		"title": "flag for Mongolia"
	},
	{
		"code": "MO",
		"emoji": "🇲🇴",
		"unicode": "U+1F1F2 U+1F1F4",
		"name": "Macao",
		"title": "flag for Macao"
	},
	{
		"code": "MP",
		"emoji": "🇲🇵",
		"unicode": "U+1F1F2 U+1F1F5",
		"name": "Northern Mariana Islands",
		"title": "flag for Northern Mariana Islands"
	},
	{
		"code": "MQ",
		"emoji": "🇲🇶",
		"unicode": "U+1F1F2 U+1F1F6",
		"name": "Martinique",
		"title": "flag for Martinique"
	},
	{
		"code": "MR",
		"emoji": "🇲🇷",
		"unicode": "U+1F1F2 U+1F1F7",
		"name": "Mauritania",
		"title": "flag for Mauritania"
	},
	{
		"code": "MS",
		"emoji": "🇲🇸",
		"unicode": "U+1F1F2 U+1F1F8",
		"name": "Montserrat",
		"title": "flag for Montserrat"
	},
	{
		"code": "MT",
		"emoji": "🇲🇹",
		"unicode": "U+1F1F2 U+1F1F9",
		"name": "Malta",
		"title": "flag for Malta"
	},
	{
		"code": "MU",
		"emoji": "🇲🇺",
		"unicode": "U+1F1F2 U+1F1FA",
		"name": "Mauritius",
		"title": "flag for Mauritius"
	},
	{
		"code": "MV",
		"emoji": "🇲🇻",
		"unicode": "U+1F1F2 U+1F1FB",
		"name": "Maldives",
		"title": "flag for Maldives"
	},
	{
		"code": "MW",
		"emoji": "🇲🇼",
		"unicode": "U+1F1F2 U+1F1FC",
		"name": "Malawi",
		"title": "flag for Malawi"
	},
	{
		"code": "MX",
		"emoji": "🇲🇽",
		"unicode": "U+1F1F2 U+1F1FD",
		"name": "Mexico",
		"title": "flag for Mexico"
	},
	{
		"code": "MY",
		"emoji": "🇲🇾",
		"unicode": "U+1F1F2 U+1F1FE",
		"name": "Malaysia",
		"title": "flag for Malaysia"
	},
	{
		"code": "MZ",
		"emoji": "🇲🇿",
		"unicode": "U+1F1F2 U+1F1FF",
		"name": "Mozambique",
		"title": "flag for Mozambique"
	},
	{
		"code": "NA",
		"emoji": "🇳🇦",
		"unicode": "U+1F1F3 U+1F1E6",
		"name": "Namibia",
		"title": "flag for Namibia"
	},
	{
		"code": "NC",
		"emoji": "🇳🇨",
		"unicode": "U+1F1F3 U+1F1E8",
		"name": "New Caledonia",
		"title": "flag for New Caledonia"
	},
	{
		"code": "NE",
		"emoji": "🇳🇪",
		"unicode": "U+1F1F3 U+1F1EA",
		"name": "Niger",
		"title": "flag for Niger"
	},
	{
		"code": "NF",
		"emoji": "🇳🇫",
		"unicode": "U+1F1F3 U+1F1EB",
		"name": "Norfolk Island",
		"title": "flag for Norfolk Island"
	},
	{
		"code": "NG",
		"emoji": "🇳🇬",
		"unicode": "U+1F1F3 U+1F1EC",
		"name": "Nigeria",
		"title": "flag for Nigeria"
	},
	{
		"code": "NI",
		"emoji": "🇳🇮",
		"unicode": "U+1F1F3 U+1F1EE",
		"name": "Nicaragua",
		"title": "flag for Nicaragua"
	},
	{
		"code": "NL",
		"emoji": "🇳🇱",
		"unicode": "U+1F1F3 U+1F1F1",
		"name": "Netherlands",
		"title": "flag for Netherlands"
	},
	{
		"code": "NO",
		"emoji": "🇳🇴",
		"unicode": "U+1F1F3 U+1F1F4",
		"name": "Norway",
		"title": "flag for Norway"
	},
	{
		"code": "NP",
		"emoji": "🇳🇵",
		"unicode": "U+1F1F3 U+1F1F5",
		"name": "Nepal",
		"title": "flag for Nepal"
	},
	{
		"code": "NR",
		"emoji": "🇳🇷",
		"unicode": "U+1F1F3 U+1F1F7",
		"name": "Nauru",
		"title": "flag for Nauru"
	},
	{
		"code": "NU",
		"emoji": "🇳🇺",
		"unicode": "U+1F1F3 U+1F1FA",
		"name": "Niue",
		"title": "flag for Niue"
	},
	{
		"code": "NZ",
		"emoji": "🇳🇿",
		"unicode": "U+1F1F3 U+1F1FF",
		"name": "New Zealand",
		"title": "flag for New Zealand"
	},
	{
		"code": "OM",
		"emoji": "🇴🇲",
		"unicode": "U+1F1F4 U+1F1F2",
		"name": "Oman",
		"title": "flag for Oman"
	},
	{
		"code": "PA",
		"emoji": "🇵🇦",
		"unicode": "U+1F1F5 U+1F1E6",
		"name": "Panama",
		"title": "flag for Panama"
	},
	{
		"code": "PE",
		"emoji": "🇵🇪",
		"unicode": "U+1F1F5 U+1F1EA",
		"name": "Peru",
		"title": "flag for Peru"
	},
	{
		"code": "PF",
		"emoji": "🇵🇫",
		"unicode": "U+1F1F5 U+1F1EB",
		"name": "French Polynesia",
		"title": "flag for French Polynesia"
	},
	{
		"code": "PG",
		"emoji": "🇵🇬",
		"unicode": "U+1F1F5 U+1F1EC",
		"name": "Papua New Guinea",
		"title": "flag for Papua New Guinea"
	},
	{
		"code": "PH",
		"emoji": "🇵🇭",
		"unicode": "U+1F1F5 U+1F1ED",
		"name": "Philippines",
		"title": "flag for Philippines"
	},
	{
		"code": "PK",
		"emoji": "🇵🇰",
		"unicode": "U+1F1F5 U+1F1F0",
		"name": "Pakistan",
		"title": "flag for Pakistan"
	},
	{
		"code": "PL",
		"emoji": "🇵🇱",
		"unicode": "U+1F1F5 U+1F1F1",
		"name": "Poland",
		"title": "flag for Poland"
	},
	{
		"code": "PM",
		"emoji": "🇵🇲",
		"unicode": "U+1F1F5 U+1F1F2",
		"name": "Saint Pierre and Miquelon",
		"title": "flag for Saint Pierre and Miquelon"
	},
	{
		"code": "PN",
		"emoji": "🇵🇳",
		"unicode": "U+1F1F5 U+1F1F3",
		"name": "Pitcairn",
		"title": "flag for Pitcairn"
	},
	{
		"code": "PR",
		"emoji": "🇵🇷",
		"unicode": "U+1F1F5 U+1F1F7",
		"name": "Puerto Rico",
		"title": "flag for Puerto Rico"
	},
	{
		"code": "PS",
		"emoji": "🇵🇸",
		"unicode": "U+1F1F5 U+1F1F8",
		"name": "Palestinian Territory",
		"title": "flag for Palestinian Territory"
	},
	{
		"code": "PT",
		"emoji": "🇵🇹",
		"unicode": "U+1F1F5 U+1F1F9",
		"name": "Portugal",
		"title": "flag for Portugal"
	},
	{
		"code": "PW",
		"emoji": "🇵🇼",
		"unicode": "U+1F1F5 U+1F1FC",
		"name": "Palau",
		"title": "flag for Palau"
	},
	{
		"code": "PY",
		"emoji": "🇵🇾",
		"unicode": "U+1F1F5 U+1F1FE",
		"name": "Paraguay",
		"title": "flag for Paraguay"
	},
	{
		"code": "QA",
		"emoji": "🇶🇦",
		"unicode": "U+1F1F6 U+1F1E6",
		"name": "Qatar",
		"title": "flag for Qatar"
	},
	{
		"code": "RE",
		"emoji": "🇷🇪",
		"unicode": "U+1F1F7 U+1F1EA",
		"name": "Réunion",
		"title": "flag for Réunion"
	},
	{
		"code": "RO",
		"emoji": "🇷🇴",
		"unicode": "U+1F1F7 U+1F1F4",
		"name": "Romania",
		"title": "flag for Romania"
	},
	{
		"code": "RS",
		"emoji": "🇷🇸",
		"unicode": "U+1F1F7 U+1F1F8",
		"name": "Serbia",
		"title": "flag for Serbia"
	},
	{
		"code": "RU",
		"emoji": "🇷🇺",
		"unicode": "U+1F1F7 U+1F1FA",
		"name": "Russia",
		"title": "flag for Russia"
	},
	{
		"code": "RW",
		"emoji": "🇷🇼",
		"unicode": "U+1F1F7 U+1F1FC",
		"name": "Rwanda",
		"title": "flag for Rwanda"
	},
	{
		"code": "SA",
		"emoji": "🇸🇦",
		"unicode": "U+1F1F8 U+1F1E6",
		"name": "Saudi Arabia",
		"title": "flag for Saudi Arabia"
	},
	{
		"code": "SB",
		"emoji": "🇸🇧",
		"unicode": "U+1F1F8 U+1F1E7",
		"name": "Solomon Islands",
		"title": "flag for Solomon Islands"
	},
	{
		"code": "SC",
		"emoji": "🇸🇨",
		"unicode": "U+1F1F8 U+1F1E8",
		"name": "Seychelles",
		"title": "flag for Seychelles"
	},
	{
		"code": "SD",
		"emoji": "🇸🇩",
		"unicode": "U+1F1F8 U+1F1E9",
		"name": "Sudan",
		"title": "flag for Sudan"
	},
	{
		"code": "SE",
		"emoji": "🇸🇪",
		"unicode": "U+1F1F8 U+1F1EA",
		"name": "Sweden",
		"title": "flag for Sweden"
	},
	{
		"code": "SG",
		"emoji": "🇸🇬",
		"unicode": "U+1F1F8 U+1F1EC",
		"name": "Singapore",
		"title": "flag for Singapore"
	},
	{
		"code": "SH",
		"emoji": "🇸🇭",
		"unicode": "U+1F1F8 U+1F1ED",
		"name": "Saint Helena, Ascension and Tristan Da Cunha",
		"title": "flag for Saint Helena, Ascension and Tristan Da Cunha"
	},
	{
		"code": "SI",
		"emoji": "🇸🇮",
		"unicode": "U+1F1F8 U+1F1EE",
		"name": "Slovenia",
		"title": "flag for Slovenia"
	},
	{
		"code": "SJ",
		"emoji": "🇸🇯",
		"unicode": "U+1F1F8 U+1F1EF",
		"name": "Svalbard and Jan Mayen",
		"title": "flag for Svalbard and Jan Mayen"
	},
	{
		"code": "SK",
		"emoji": "🇸🇰",
		"unicode": "U+1F1F8 U+1F1F0",
		"name": "Slovakia",
		"title": "flag for Slovakia"
	},
	{
		"code": "SL",
		"emoji": "🇸🇱",
		"unicode": "U+1F1F8 U+1F1F1",
		"name": "Sierra Leone",
		"title": "flag for Sierra Leone"
	},
	{
		"code": "SM",
		"emoji": "🇸🇲",
		"unicode": "U+1F1F8 U+1F1F2",
		"name": "San Marino",
		"title": "flag for San Marino"
	},
	{
		"code": "SN",
		"emoji": "🇸🇳",
		"unicode": "U+1F1F8 U+1F1F3",
		"name": "Senegal",
		"title": "flag for Senegal"
	},
	{
		"code": "SO",
		"emoji": "🇸🇴",
		"unicode": "U+1F1F8 U+1F1F4",
		"name": "Somalia",
		"title": "flag for Somalia"
	},
	{
		"code": "SR",
		"emoji": "🇸🇷",
		"unicode": "U+1F1F8 U+1F1F7",
		"name": "Suriname",
		"title": "flag for Suriname"
	},
	{
		"code": "SS",
		"emoji": "🇸🇸",
		"unicode": "U+1F1F8 U+1F1F8",
		"name": "South Sudan",
		"title": "flag for South Sudan"
	},
	{
		"code": "ST",
		"emoji": "🇸🇹",
		"unicode": "U+1F1F8 U+1F1F9",
		"name": "Sao Tome and Principe",
		"title": "flag for Sao Tome and Principe"
	},
	{
		"code": "SV",
		"emoji": "🇸🇻",
		"unicode": "U+1F1F8 U+1F1FB",
		"name": "El Salvador",
		"title": "flag for El Salvador"
	},
	{
		"code": "SX",
		"emoji": "🇸🇽",
		"unicode": "U+1F1F8 U+1F1FD",
		"name": "Sint Maarten (Dutch Part)",
		"title": "flag for Sint Maarten (Dutch Part)"
	},
	{
		"code": "SY",
		"emoji": "🇸🇾",
		"unicode": "U+1F1F8 U+1F1FE",
		"name": "Syrian Arab Republic",
		"title": "flag for Syrian Arab Republic"
	},
	{
		"code": "SZ",
		"emoji": "🇸🇿",
		"unicode": "U+1F1F8 U+1F1FF",
		"name": "Swaziland",
		"title": "flag for Swaziland"
	},
	{
		"code": "TC",
		"emoji": "🇹🇨",
		"unicode": "U+1F1F9 U+1F1E8",
		"name": "Turks and Caicos Islands",
		"title": "flag for Turks and Caicos Islands"
	},
	{
		"code": "TD",
		"emoji": "🇹🇩",
		"unicode": "U+1F1F9 U+1F1E9",
		"name": "Chad",
		"title": "flag for Chad"
	},
	{
		"code": "TF",
		"emoji": "🇹🇫",
		"unicode": "U+1F1F9 U+1F1EB",
		"name": "French Southern Territories",
		"title": "flag for French Southern Territories"
	},
	{
		"code": "TG",
		"emoji": "🇹🇬",
		"unicode": "U+1F1F9 U+1F1EC",
		"name": "Togo",
		"title": "flag for Togo"
	},
	{
		"code": "TH",
		"emoji": "🇹🇭",
		"unicode": "U+1F1F9 U+1F1ED",
		"name": "Thailand",
		"title": "flag for Thailand"
	},
	{
		"code": "TJ",
		"emoji": "🇹🇯",
		"unicode": "U+1F1F9 U+1F1EF",
		"name": "Tajikistan",
		"title": "flag for Tajikistan"
	},
	{
		"code": "TK",
		"emoji": "🇹🇰",
		"unicode": "U+1F1F9 U+1F1F0",
		"name": "Tokelau",
		"title": "flag for Tokelau"
	},
	{
		"code": "TL",
		"emoji": "🇹🇱",
		"unicode": "U+1F1F9 U+1F1F1",
		"name": "Timor-Leste",
		"title": "flag for Timor-Leste"
	},
	{
		"code": "TM",
		"emoji": "🇹🇲",
		"unicode": "U+1F1F9 U+1F1F2",
		"name": "Turkmenistan",
		"title": "flag for Turkmenistan"
	},
	{
		"code": "TN",
		"emoji": "🇹🇳",
		"unicode": "U+1F1F9 U+1F1F3",
		"name": "Tunisia",
		"title": "flag for Tunisia"
	},
	{
		"code": "TO",
		"emoji": "🇹🇴",
		"unicode": "U+1F1F9 U+1F1F4",
		"name": "Tonga",
		"title": "flag for Tonga"
	},
	{
		"code": "TR",
		"emoji": "🇹🇷",
		"unicode": "U+1F1F9 U+1F1F7",
		"name": "Turkey",
		"title": "flag for Turkey"
	},
	{
		"code": "TT",
		"emoji": "🇹🇹",
		"unicode": "U+1F1F9 U+1F1F9",
		"name": "Trinidad and Tobago",
		"title": "flag for Trinidad and Tobago"
	},
	{
		"code": "TV",
		"emoji": "🇹🇻",
		"unicode": "U+1F1F9 U+1F1FB",
		"name": "Tuvalu",
		"title": "flag for Tuvalu"
	},
	{
		"code": "TW",
		"emoji": "🇹🇼",
		"unicode": "U+1F1F9 U+1F1FC",
		"name": "Taiwan",
		"title": "flag for Taiwan"
	},
	{
		"code": "TZ",
		"emoji": "🇹🇿",
		"unicode": "U+1F1F9 U+1F1FF",
		"name": "Tanzania",
		"title": "flag for Tanzania"
	},
	{
		"code": "UA",
		"emoji": "🇺🇦",
		"unicode": "U+1F1FA U+1F1E6",
		"name": "Ukraine",
		"title": "flag for Ukraine"
	},
	{
		"code": "UG",
		"emoji": "🇺🇬",
		"unicode": "U+1F1FA U+1F1EC",
		"name": "Uganda",
		"title": "flag for Uganda"
	},
	{
		"code": "UM",
		"emoji": "🇺🇲",
		"unicode": "U+1F1FA U+1F1F2",
		"name": "United States Minor Outlying Islands",
		"title": "flag for United States Minor Outlying Islands"
	},
	{
		"code": "US",
		"emoji": "🇺🇸",
		"unicode": "U+1F1FA U+1F1F8",
		"name": "United States",
		"title": "flag for United States"
	},
	{
		"code": "UY",
		"emoji": "🇺🇾",
		"unicode": "U+1F1FA U+1F1FE",
		"name": "Uruguay",
		"title": "flag for Uruguay"
	},
	{
		"code": "UZ",
		"emoji": "🇺🇿",
		"unicode": "U+1F1FA U+1F1FF",
		"name": "Uzbekistan",
		"title": "flag for Uzbekistan"
	},
	{
		"code": "VA",
		"emoji": "🇻🇦",
		"unicode": "U+1F1FB U+1F1E6",
		"name": "Vatican City",
		"title": "flag for Vatican City"
	},
	{
		"code": "VC",
		"emoji": "🇻🇨",
		"unicode": "U+1F1FB U+1F1E8",
		"name": "Saint Vincent and The Grenadines",
		"title": "flag for Saint Vincent and The Grenadines"
	},
	{
		"code": "VE",
		"emoji": "🇻🇪",
		"unicode": "U+1F1FB U+1F1EA",
		"name": "Venezuela",
		"title": "flag for Venezuela"
	},
	{
		"code": "VG",
		"emoji": "🇻🇬",
		"unicode": "U+1F1FB U+1F1EC",
		"name": "Virgin Islands, British",
		"title": "flag for Virgin Islands, British"
	},
	{
		"code": "VI",
		"emoji": "🇻🇮",
		"unicode": "U+1F1FB U+1F1EE",
		"name": "Virgin Islands, U.S.",
		"title": "flag for Virgin Islands, U.S."
	},
	{
		"code": "VN",
		"emoji": "🇻🇳",
		"unicode": "U+1F1FB U+1F1F3",
		"name": "Viet Nam",
		"title": "flag for Viet Nam"
	},
	{
		"code": "VU",
		"emoji": "🇻🇺",
		"unicode": "U+1F1FB U+1F1FA",
		"name": "Vanuatu",
		"title": "flag for Vanuatu"
	},
	{
		"code": "WF",
		"emoji": "🇼🇫",
		"unicode": "U+1F1FC U+1F1EB",
		"name": "Wallis and Futuna",
		"title": "flag for Wallis and Futuna"
	},
	{
		"code": "WS",
		"emoji": "🇼🇸",
		"unicode": "U+1F1FC U+1F1F8",
		"name": "Samoa",
		"title": "flag for Samoa"
	},
	{
		"code": "YE",
		"emoji": "🇾🇪",
		"unicode": "U+1F1FE U+1F1EA",
		"name": "Yemen",
		"title": "flag for Yemen"
	},
	{
		"code": "YT",
		"emoji": "🇾🇹",
		"unicode": "U+1F1FE U+1F1F9",
		"name": "Mayotte",
		"title": "flag for Mayotte"
	},
	{
		"code": "ZA",
		"emoji": "🇿🇦",
		"unicode": "U+1F1FF U+1F1E6",
		"name": "South Africa",
		"title": "flag for South Africa"
	},
	{
		"code": "ZM",
		"emoji": "🇿🇲",
		"unicode": "U+1F1FF U+1F1F2",
		"name": "Zambia",
		"title": "flag for Zambia"
	},
	{
		"code": "ZW",
		"emoji": "🇿🇼",
		"unicode": "U+1F1FF U+1F1FC",
		"name": "Zimbabwe",
		"title": "flag for Zimbabwe"
	}
]

data = {}
for flag in flags:
	data[flag['code']] = flag['emoji']

def lookup(country_code):
	if country_code in data:
		return data[country_code.upper()]
	return None
	

def chunks(l,n):
	for i in range(0, len(l), n):
		yield l[i:i + n]
