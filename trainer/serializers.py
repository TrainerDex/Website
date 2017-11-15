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

class DiscordServerSerializer(serializers.ModelSerializer):
	owner = serializers.SerializerMethodField()
	warning = serializers.SerializerMethodField()
	
	def get_owner(self, obj):
		return SocialAccount.objects.filter(provider='discord', user=obj.owner)[0].uid
	
	def get_warning(self, obj):
		return '/api/0.1/discord/servers/ has been deprecated. Please use /api/0.2/guilds/. Also, owner may not be 100% accurate if the server owner has multiple Discord accounts. Not for validation.'
	
	class Meta:
		model = DiscordGuild
		fields = '__all__'

class DiscordGuildSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscordGuild
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
	
