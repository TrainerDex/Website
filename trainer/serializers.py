# -*- coding: utf-8 -*-
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from cities.models import Country, Region
from django.contrib.auth.models import User
from trainer.models import *
from trainer.shortcuts import level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES

class BriefUpdateSerializer(serializers.ModelSerializer):
	xp = serializers.SerializerMethodField()
	
	def get_xp(self, obj):
		return obj.total_xp
	
	class Meta:
		model = Update
		fields = ('uuid', 'trainer', 'update_time', 'xp', 'total_xp', 'modified_extra_fields')

class DetailedUpdateSerializer(serializers.ModelSerializer):
	xp = serializers.SerializerMethodField()
	
	def get_xp(self, obj):
		return obj.total_xp
	
	def validate(self, attrs):
		instance = Update(**attrs)
		instance.clean()
		return attrs
	
	class Meta:
		model = Update
		fields = ('uuid', 'trainer', 'update_time', 'xp', 'total_xp', 'pokedex_caught', 'pokedex_seen', 'gymbadges_total', 'gymbadges_gold', 'pokemon_info_stardust',) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('data_source',)

class BriefTrainerSerializer(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'leaderboard_country', 'leaderboard_region', 'update_set', 'prefered')

class DetailedTrainerSerializer(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'badge_chicago_fest_july_2017', 'badge_pikachu_outbreak_yokohama_2017', 'badge_safari_zone_europe_2017_09_16', 'badge_safari_zone_europe_2017_10_07', 'badge_safari_zone_europe_2017_10_14', 'leaderboard_country', 'leaderboard_region', 'badge_chicago_fest_july_2018', 'badge_apac_partner_july_2018_japan', 'badge_apac_partner_july_2018_south_korea', 'update_set', 'prefered', 'verified')

class DetailedTrainerSerializerPATCH(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		read_only_fields = ('id', 'owner', 'username', 'faction')
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'last_cheated', 'daily_goal', 'total_goal', 'badge_chicago_fest_july_2017', 'badge_pikachu_outbreak_yokohama_2017', 'badge_safari_zone_europe_2017_09_16', 'badge_safari_zone_europe_2017_10_07', 'badge_safari_zone_europe_2017_10_14', 'leaderboard_country', 'leaderboard_region', 'badge_chicago_fest_july_2018', 'badge_apac_partner_july_2018_japan', 'badge_apac_partner_july_2018_south_korea', 'update_set', 'prefered', 'verified')

class UserSerializer(serializers.ModelSerializer):
	profiles = serializers.SerializerMethodField()
	
	def get_profiles(self, obj):
		return [obj.trainer.pk]
	
	def create(self, validated_data):
		user = User.objects.create_user(**validated_data)
		return user
	
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name', 'profiles')
		read_only_fields = ('profiles',)

class FactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Faction
		fields = ('id', 'name_en',)

class LeaderboardSerializer(serializers.Serializer):
	level = serializers.SerializerMethodField()
	position = serializers.SerializerMethodField()
	id = serializers.SerializerMethodField()
	username = serializers.SerializerMethodField()
	faction = serializers.SerializerMethodField()
	xp = serializers.SerializerMethodField()
	last_updated = serializers.SerializerMethodField()
	user_id = serializers.SerializerMethodField()
	
	def get_position(self, obj):
		return obj[0]
	
	def get_level(self, obj):
		return obj[1].level()
	
	def get_id(self, obj):
		return obj[1].id
	
	def get_username(self, obj):
		return obj[1].username
	
	def get_faction(self, obj):
		return FactionSerializer(obj[1].faction).data
	
	def get_xp(self, obj):
		return obj[1].update__total_xp__max
	
	def get_last_updated(self, obj):
		return obj[1].update__update_time__max
	
	def get_user_id(self, obj):
		return obj[1].owner.pk if obj[1].owner else None
	
	class Meta:
		model = Trainer
		fields = ('position', 'id', 'username', 'faction', 'level', 'xp', 'last_updated', 'user_id')

class SocialAllAuthSerializer(serializers.ModelSerializer):
	
	trainer = serializers.SerializerMethodField()
	
	def get_trainer(self, obj):
		return obj.user.trainer.pk
	
	class Meta:
		model = SocialAccount
		fields = ('user', 'provider', 'uid', 'extra_data', 'trainer',)
