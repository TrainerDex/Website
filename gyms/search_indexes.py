from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, Float, Boolean
 
class GymIndex(DocType):
    enabled = Boolean()
    guard_pokemon_id = Integer()
    id = Text()
    last_modified = Date()
    last_scanned = Date()
    latitude = Float()
    longitude = Float()
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    description = Text()
    image = Text()
    team = Integer()
    slots_available = Integer()
    raid_start = Date()
    raid_end = Date()
    raid_level = Integer()
    raid_pokemon_id = Integer()
    raid_pokemon_name = Text()
    raid_pokemon_cp = Integer()
    raid_pokemon_move_1 = Integer()
    raid_pokemon_move_2 = Integer()

    class Meta:
        index = 'gym'
