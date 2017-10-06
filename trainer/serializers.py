# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class ExtendedProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExtendedProfile
		fields = ('dob', )
		
class UpdateSerializer(serializers.ModelSerializer):
#	owner = serializers.ReadOnlyField(source='owner.username')
	
	class Meta:
		model = Update
		fields = '__all__'

class TrainerSerializer(serializers.ModelSerializer):
	update = serializers.SerializerMethodField()
	
	def get_update(self, obj):
		return UpdateSerializer(obj.update_set.order_by('datetime').last()).data
	
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
	class Meta:
		model = DiscordUser
		fields = '__all__'
		
class DiscordMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscordMember
		fields = '__all__'
		

class NetworkSerializer(serializers.ModelSerializer):
	class Meta:
		model = Network
		fields = '__all__'
		
class NetworkMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = NetworkMember
		fields = '__all__'
		
class BanSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ban
		fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = '__all__'