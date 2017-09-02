from rest_framework import serializers
from .models import *

class Factions_Serializer(serializers.ModelSerializer):
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
		model = Discord_Users
		fields = '__all__'
		
class Discord_Relations_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discord_Relations
		fields = '__all__'
		
class Discord_Servers_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discord_Servers
		fields = '__all__'