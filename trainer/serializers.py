# -*- coding: utf-8 -*-
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from cities.models import Country, Region
from django.contrib.auth.models import User
from trainer.models import *
from trainer.shortcuts import level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES

class BriefUpdateSerializer(serializers.ModelSerializer):
	altered_fields = serializers.SerializerMethodField()
	
	def get_altered_fields(self, obj):
		changed_list = []
		field_list = ('dex_caught', 'dex_seen', 'gym_badges') + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES
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
		fields = ('uuid', 'trainer', 'update_time', 'xp', 'dex_caught', 'dex_seen', 'gym_badges',) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('meta_source',)

class BriefTrainerSerializer(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'leaderboard_country', 'leaderboard_region', 'update_set', 'prefered')

class DetailedTrainerSerializer(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'go_fest_2017', 'outbreak_2017', 'safari_zone_2017_oberhausen', 'safari_zone_2017_paris', 'safari_zone_2017_barcelona', 'safari_zone_2017_copenhagen', 'safari_zone_2017_prague', 'safari_zone_2017_stockholm', 'safari_zone_2017_amstelveen', 'leaderboard_country', 'leaderboard_region', 'update_set', 'prefered', 'verified')

class DetailedTrainerSerializerPATCH(serializers.ModelSerializer):
	update_set = BriefUpdateSerializer(read_only=True, many=True)
	prefered = serializers.SerializerMethodField()
	
	def get_prefered(self, obj):
		return True
	
	class Meta:
		model = Trainer
		read_only_fields = ('id', 'owner', 'username', 'faction')
		fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'go_fest_2017', 'outbreak_2017', 'safari_zone_2017_oberhausen', 'safari_zone_2017_paris', 'safari_zone_2017_barcelona', 'safari_zone_2017_copenhagen', 'safari_zone_2017_prague', 'safari_zone_2017_stockholm', 'safari_zone_2017_amstelveen', 'leaderboard_country', 'leaderboard_region', 'update_set', 'prefered', 'verified')

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
		fields = ('id', 'name', 'colour')

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
		return level_parser(xp=obj[1].update__xp__max).level
	
	def get_id(self, obj):
		return obj[1].id
	
	def get_username(self, obj):
		return obj[1].username
	
	def get_faction(self, obj):
		return FactionSerializer(obj[1].faction).data
	
	def get_xp(self, obj):
		return obj[1].update__xp__max
	
	def get_last_updated(self, obj):
		return obj[1].update__update_time__max
	
	def get_user_id(self, obj):
		return obj[1].owner.pk if obj[1].owner else None
	
	class Meta:
		model = Trainer
		fields = ('position', 'id', 'username', 'faction', 'level', 'xp', 'last_updated', 'user_id')

class SocialAllAuthSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = SocialAccount
		fields = ('user', 'provider', 'uid', 'extra_data')
