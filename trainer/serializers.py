from rest_framework import serializers
from django.contrib.auth.models import User
from trainer.models import *

class ExtendedProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExtendedProfile
		fields = ('dob', 'prefered_profile')

class BriefUpdateSerializer(serializers.ModelSerializer):
	altered_fields = serializers.SerializerMethodField()
	
	def get_altered_fields(self, obj):
		changed_list = []
		field_list = ('dex_caught', 'dex_seen', 'gym_badges', 'walk_dist', 'gen_1_dex', 'pkmn_caught', 'pkmn_evolved', 'eggs_hatched', 'pkstops_spun', 'big_magikarp', 'battles_won', 'legacy_gym_trained', 'tiny_rattata', 'pikachu_caught', 'gen_2_dex', 'unown_alphabet', 'berry_fed', 'gym_defended', 'raids_completed', 'leg_raids_completed', 'gen_3_dex', 'pkmn_normal', 'pkmn_flying', 'pkmn_poison', 'pkmn_ground', 'pkmn_rock', 'pkmn_bug', 'pkmn_steel', 'pkmn_fire', 'pkmn_water', 'pkmn_grass', 'pkmn_electric', 'pkmn_psychic', 'pkmn_dark', 'pkmn_fairy', 'pkmn_fighting', 'pkmn_ghost', 'pkmn_ice', 'pkmn_dragon')
		for k, v in obj.__dict__.items():
			if k in field_list and v is not None:
				changed_list.append(k)
		return changed_list
	
	class Meta:
		model = Update
		fields = ('uuid', 'trainer', 'update_time', 'xp', 'altered_fields')

class DetailedUpdateSerializer(serializers.ModelSerializer):
	
	def validate(self, attrs):
		instance = Update(**attrs)
		instance.clean()
		return attrs
	
	class Meta:
		model = Update
		fields = ('uuid', 'trainer', 'update_time', 'xp', 'dex_caught', 'dex_seen', 'gym_badges', 'walk_dist', 'gen_1_dex', 'pkmn_caught', 'pkmn_evolved', 'eggs_hatched', 'pkstops_spun', 'big_magikarp', 'battles_won', 'legacy_gym_trained', 'tiny_rattata', 'pikachu_caught', 'gen_2_dex', 'unown_alphabet', 'berry_fed', 'gym_defended', 'raids_completed', 'leg_raids_completed', 'gen_3_dex', 'pkmn_normal', 'pkmn_flying', 'pkmn_poison', 'pkmn_ground', 'pkmn_rock', 'pkmn_bug', 'pkmn_steel', 'pkmn_fire', 'pkmn_water', 'pkmn_grass', 'pkmn_electric', 'pkmn_psychic', 'pkmn_dark', 'pkmn_fairy', 'pkmn_fighting', 'pkmn_ghost', 'pkmn_ice', 'pkmn_dragon')

class BriefTrainerSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal')

class DetailedTrainerSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'go_fest_2017', 'outbreak_2017', 'safari_zone_2017_oberhausen', 'safari_zone_2017_paris', 'safari_zone_2017_barcelona', 'safari_zone_2017_copenhagen', 'safari_zone_2017_prague', 'safari_zone_2017_stockholm', 'safari_zone_2017_amstelveen')

class UserSerializer(serializers.ModelSerializer):
	extra = serializers.SerializerMethodField()
	
	def get_extra(self, obj):
		return ExtendedProfileSerializer(ExtendedProfile.objects.get(user=obj)).data
	
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name', 'extra')

class FactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Faction
		fields = '__all__'
