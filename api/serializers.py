from rest_framework import serializers
from api.models import *

class Faction_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Factions
		fields = '__all__'

class Trainer_Levels_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Trainer_Levels
		fields = '__all__'
		
class Trainer_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Trainer
		fields = '__all__'
		
class Experience_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Experience
		fields = '__all__'
		
class Discord_Users_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discordian
		fields = '__all__'
		
class Discord_Users_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discordian_On_Servers
		fields = '__all__'
		
class Discord_Servers_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Servers
		fields = '__all__'