# -*- coding: utf-8 -*-
import json
from rest_framework import serializers
from django.contrib.auth.models import User
from trainer.models import *
from allauth.socialaccount.models import SocialAccount

class ExtendedProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExtendedProfile
		fields = ('dob', )

class UpdateSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Update
		fields = '__all__'

class TrainerSerializer(serializers.ModelSerializer):
	update = serializers.SerializerMethodField()
	updates = serializers.SerializerMethodField()
	
	def get_update(self, obj):
		return UpdateSerializer(obj.update_set.order_by('-datetime').first()).data
	
	def get_updates(self, obj):
		return UpdateSerializer(obj.update_set.order_by('-datetime').all(), many=True).data
	
	class Meta:
		model = Trainer
		fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
	profiles = TrainerSerializer(many=True, read_only=True)
#	extended_profile = ExtendedProfileSerializer()
		
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name', 'profiles')

class FactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Faction
		fields = '__all__'

class DiscordServerSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscordServer
		fields = '__all__'

class DiscordUserSerializer(serializers.ModelSerializer):
	account = serializers.ReadOnlyField(source='user.id')
	id = serializers.ReadOnlyField(source='uid')
	name = serializers.SerializerMethodField()
	discriminator = serializers.SerializerMethodField()
	avatar_url = serializers.SerializerMethodField()
	creation = serializers.ReadOnlyField(source='date_joined')
	ref = serializers.ReadOnlyField(source='id')
	
	def get_name(self, obj):
		try:
			return obj.extra_data['username']
		except KeyError:
			return ''
	
	def get_discriminator(self, obj):
		try:
			return obj.extra_data['discriminator']
		except KeyError:
			return ''
	
	def get_avatar_url(self, obj):
		try:
			if obj.extra_data['avatar']:
				return 'https://cdn.discordapp.com/avatars/{}/{}.png'.format(obj.uid, obj.extra_data['avatar'])
			else:
				return ''
		except KeyError:
			return ''
	
	class Meta:
		model = SocialAccount
		fields = ('account', 'id', 'name', 'discriminator', 'creation', 'avatar_url', 'ref')
	
