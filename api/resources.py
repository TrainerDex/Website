from tastypie.resources import ModelResource
from api.models import *

class Trainer_Levels_Resource(ModelResource):
	class Meta:
		queryset = Trainer_Levels.objects.all()
		resource_name = 'levels'
		
class Trainers_Resource(ModelResource):
	class Meta:
		queryset = Trainers.objects.all()
		resource_name = 'trainers'
		
class Experience_Resource(ModelResource):
	class Meta:
		queryset = Experience.objects.all()
		resource_name = 'xp'
		
class Discordian_Resource(ModelResource):
	class Meta:
		queryset = Discordian.objects.all()
		resource_name = 'discordUsers'
		
class Discordian_On_Servers_Resource(ModelResource):
	class Meta:
		queryset = Discordian_On_Servers.objects.all()
		resource_name = 'discordMembers'
		
class Servers_Resource(ModelResource):
	class Meta:
		queryset = Servers.objects.all()
		resource_name = 'discordServers'