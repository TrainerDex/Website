# -*- coding: utf-8 -*-
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from pokemongo.models import Update, Trainer, Faction
from pokemongo.shortcuts import level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES

class BriefUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.SerializerMethodField()
    
    def get_xp(self, obj):
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp
    
    class Meta:
        model = Update
        fields = ('uuid', 'trainer', 'update_time', 'xp', 'total_xp', 'modified_extra_fields')

class DetailedUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.SerializerMethodField()
    
    def get_xp(self, obj):
        """This field is deprecated and will be removed in API v2"""
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
    username = serializers.SerializerMethodField()
    
    def get_prefered(self, obj):
        """This field is deprecated and will be removed in API v2"""
        return True
    
    def get_username(self, obj):
        return obj.nickname
    
    class Meta:
        model = Trainer
        fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'leaderboard_country', 'leaderboard_region', 'update_set', 'prefered', 'statistics')

class DetailedTrainerSerializer(serializers.ModelSerializer):
    update_set = BriefUpdateSerializer(read_only=True, many=True)
    prefered = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    
    def get_prefered(self, obj):
        """This field is deprecated and will be removed in API v2"""
        return True
    
    def get_username(self, obj):
        return obj.nickname
    
    class Meta:
        model = Trainer
        fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'has_cheated', 'last_cheated', 'currently_cheats', 'daily_goal', 'total_goal', 'update_set', 'prefered', 'verified', 'statistics')

class DetailedTrainerSerializerPATCH(serializers.ModelSerializer):
    update_set = BriefUpdateSerializer(read_only=True, many=True)
    prefered = serializers.SerializerMethodField()
    
    def get_prefered(self, obj):
        """This field is deprecated and will be removed in API v2"""
        return True
    
    class Meta:
        model = Trainer
        read_only_fields = ('id', 'owner', 'username', 'faction')
        fields = ('id', 'last_modified', 'owner', 'username', 'start_date', 'faction', 'trainer_code', 'last_cheated', 'daily_goal', 'total_goal', 'badge_chicago_fest_july_2017', 'badge_pikachu_outbreak_yokohama_2017', 'badge_safari_zone_europe_2017_09_16', 'badge_safari_zone_europe_2017_10_07', 'badge_safari_zone_europe_2017_10_14', 'leaderboard_country', 'leaderboard_region', 'badge_chicago_fest_july_2018', 'badge_apac_partner_july_2018_japan', 'badge_apac_partner_july_2018_south_korea', 'update_set', 'prefered', 'verified', 'statistics')

class UserSerializer(serializers.ModelSerializer):
    profiles = serializers.SerializerMethodField()
    
    def get_profiles(self, obj):
        """This field is deprecated and will be removed in API v2"""
        try:
            return [obj.trainer.pk]
        except User.trainer.RelatedObjectDoesNotExist:
            return []
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'profiles', 'trainer')
        read_only_fields = ('profiles','trainer')

class FactionSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name_en = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        return Faction(obj).id
    
    def get_name_en(self, obj):
        from django.utils import translation
        lang = translation.get_language()
        translation.activate("en")
        result = str(Faction(obj))
        translation.activate(lang)
        return result

class LeaderboardSerializer(serializers.Serializer):
    level = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    faction = serializers.SerializerMethodField()
    xp = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    
    def get_position(self, obj):
        return obj.rank
    
    def get_level(self, obj):
        try:
            return level_parser(xp=obj.update__total_xp__max).level
        except ValueError:
            return None
    
    def get_id(self, obj):
        return obj.id
    
    def get_username(self, obj):
        return obj.nickname
    
    def get_faction(self, obj):
        return FactionSerializer(obj.faction).data
    
    def get_xp(self, obj):
        """This field is deprecated and will be removed in API v2"""
        return obj.update__total_xp__max
    
    def get_total_xp(self, obj):
        return obj.update__total_xp__max
    
    def get_last_updated(self, obj):
        return obj.update__update_time__max
    
    def get_user_id(self, obj):
        return obj.owner.pk if obj.owner else None
    
    class Meta:
        model = Trainer
        fields = ('position', 'id', 'username', 'faction', 'level', 'xp', 'total_xp', 'last_updated', 'user_id')

class SocialAllAuthSerializer(serializers.ModelSerializer):
    
    trainer = serializers.SerializerMethodField()
    
    def get_trainer(self, obj):
        return obj.user.trainer.pk
    
    class Meta:
        model = SocialAccount
        fields = ('user', 'provider', 'uid', 'extra_data', 'trainer',)
