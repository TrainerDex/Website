from rest_framework import serializers
from django.contrib.auth.models import User
from trainer.models import *

class ExtendedProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExtendedProfile
		fields = ('dob', 'prefered_profile')

class UpdateSerializer(serializers.ModelSerializer):
	owner = serializers.ReadOnlyField(source='trainer.owner.id')
	
	class Meta:
		model = Update
		fields = '__all__'

class TrainerSerializer(serializers.ModelSerializer):
	account = serializers.ReadOnlyField(source='owner.id')
	
	class Meta:
		model = Trainer
		fields = '__all__'

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

