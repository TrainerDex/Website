from rest_framework import serializers
from .models import *

class Faction_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Faction
		fields = '__all__'

class Trainer_Level_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Trainer_Level
		fields = '__all__'
		
class Trainer_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Trainer
		fields = '__all__'
		
class Update_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Update
		fields = '__all__'
		
class Discord_User_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discord_User
		fields = '__all__'
		
class Discord_Relation_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discord_Relation
		fields = '__all__'
		
class Discord_Server_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Discord_Server
		fields = '__all__'