from rest_framework import serializers
from django.contrib.auth.models import User
from trainer.models import *
from allauth.socialaccount.models import SocialAccount

class ExtendedProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExtendedProfile
		fields = ('dob', )

class UpdateSerializer(serializers.ModelSerializer):
	owner = serializers.ReadOnlyField(source='trainer.owner.id')
	
	class Meta:
		model = Update
		fields = '__all__'

class TrainerSerializer(serializers.ModelSerializer):
	update = serializers.SerializerMethodField()
	updates = serializers.SerializerMethodField()
	account = serializers.ReadOnlyField(source='owner.id')
	
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

class DiscordGuildSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscordGuild
		fields = '__all__'
