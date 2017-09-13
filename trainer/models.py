import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from colorful.fields import RGBColorField

def factionImagePath(instance, filename):
	return os.path.join('media/factionLogo', filename)

def leaderImagePath(instance, filename):
	return os.path.join('media/factionLeader', filename)

class ExtendedProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='extended_profile')
	dob = models.DateField(null=True, blank=True, verbose_name="date of birth")
	
	def __str__(self):
		return self.user.username

class Trainer(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
	username = models.CharField(max_length=30, unique=True)
	start_date = models.DateField(default=date(2016,7,13), null=True, blank=True)
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, null=True, verbose_name="team")
	has_cheated = models.BooleanField(default=False)
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False)
	statistics = models.BooleanField(default=True)
	daily_goal = models.IntegerField(null=True, blank=True)
	total_goal = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	prefered = models.BooleanField(default=True, verbose_name="main profile")
	
	def __str__(self):
		return self.username

class Faction(models.Model):
	name = models.CharField(max_length=140)
	colour = RGBColorField(default='#929292', null=True, blank=True)
	image = models.ImageField(upload_to=factionImagePath, blank=True, null=True)
	leader_name = models.CharField(max_length=140, null=True, blank=True)
	leader_image = models.ImageField(upload_to=leaderImagePath, blank=True, null=True)
	
	def __str__(self):
		return self.name

class Update(models.Model):
	trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	xp = models.IntegerField(verbose_name='Total XP')
	dex_caught = models.IntegerField(null=True, blank=True)
	dex_seen = models.IntegerField(null=True, blank=True)
	walk_dist = models.DecimalField(max_digits=16, decimal_places=1, null=True, blank=True)
	gen_1_dex = models.IntegerField(null=True, blank=True)
	pkmn_caught = models.IntegerField(null=True, blank=True)
	pkmn_evolved = models.IntegerField(null=True, blank=True)
	pkstops_spun = models.IntegerField(null=True, blank=True)
	battles_won = models.IntegerField(null=True, blank=True)
	gen_2_dex = models.IntegerField(null=True, blank=True)
	berry_fed = models.IntegerField(null=True, blank=True)
	gym_defended = models.IntegerField(null=True, blank=True)
	eggs_hatched = models.IntegerField(null=True, blank=True)
	big_magikarp = models.IntegerField(null=True, blank=True)
	legacy_gym_trained = models.IntegerField(null=True, blank=True)
	tiny_rattata = models.IntegerField(null=True, blank=True)
	pikachu_caught = models.IntegerField(null=True, blank=True)
	unown_alphabet = models.IntegerField(null=True, blank=True)
	raids_completed = models.IntegerField(null=True, blank=True)
	#Pokemon-demographics
	pkmn_normal = models.IntegerField(null=True, blank=True)
	pkmn_flying = models.IntegerField(null=True, blank=True)
	pkmn_poison = models.IntegerField(null=True, blank=True)
	pkmn_ground = models.IntegerField(null=True, blank=True)
	pkmn_rock = models.IntegerField(null=True, blank=True)
	pkmn_bug = models.IntegerField(null=True, blank=True)
	pkmn_steel = models.IntegerField(null=True, blank=True)
	pkmn_fire = models.IntegerField(null=True, blank=True)
	pkmn_water = models.IntegerField(null=True, blank=True)
	pkmn_grass = models.IntegerField(null=True, blank=True)
	pkmn_electric = models.IntegerField(null=True, blank=True)
	pkmn_psychic = models.IntegerField(null=True, blank=True)
	pkmn_dark = models.IntegerField(null=True, blank=True)
	pkmn_fairy = models.IntegerField(null=True, blank=True)
	pkmn_fighting = models.IntegerField(null=True, blank=True)
	pkmn_ghost = models.IntegerField(null=True, blank=True)
	pkmn_ice = models.IntegerField(null=True, blank=True)
	pkmn_dragon = models.IntegerField(null=True, blank=True)
	#Other stats
	gym_badges = models.IntegerField(null=True, blank=True)
	
	def __str__(self):
		return self.trainer.username+' '+str(self.xp)+' '+str(self.datetime)
	
class DiscordUser(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='discord_account')
	name = models.CharField(max_length=32)
	discriminator = models.CharField(max_length=4, blank=False)
	id = models.CharField(max_length=4, primary_key=True)
	avatar_url = models.URLField()
	creation = models.DateTimeField()
	
	def __str__(self):
		return self.name+'#'+str(self.discriminator)

class DiscordServer(models.Model):
	name = models.CharField(max_length=256)
	region = models.CharField(max_length=256)
	id = models.CharField(max_length=256, primary_key=True)
	icon = models.CharField(max_length=256)
	owner = models.ForeignKey('DiscordUser', on_delete=models.SET_NULL, null=True, blank=True)
	members = models.ManyToManyField('DiscordUser', through='DiscordMember', related_name='discord_members')
	bans_cheaters = models.BooleanField(default=True)
	seg_cheaters = models.BooleanField(default=False)
	bans_minors = models.BooleanField(default=False)
	seg_minors = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

class DiscordMember(models.Model):
	user = models.ForeignKey('DiscordUser', on_delete=models.CASCADE)
	server = models.ForeignKey('DiscordServer', on_delete=models.CASCADE)
	join = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return str(self.user)
	
class Network(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=256)
	discord_servers = models.ManyToManyField('DiscordServer', related_name='network_discord')
	members = models.ManyToManyField(User, through='NetworkMember', related_name='network_members')
	banned_users = models.ManyToManyField('DiscordUser', through='Ban', related_name='banned_network_members')
	
	def __str__(self):
		return self.name
	
class NetworkMember(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	network = models.ForeignKey('Network', on_delete=models.CASCADE)
	join = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.user.username
	
class Ban(models.Model):
	user = models.ForeignKey('DiscordUser', on_delete=models.CASCADE)
	discord = models.ForeignKey('DiscordServer', on_delete=models.CASCADE, null=True, blank=True)
	network = models.ForeignKey('Network', on_delete=models.CASCADE, null=True, blank=True)
	reason = models.CharField(max_length=140)
	datetime = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return str(self.user)
	
	def clean(self):
		if (self.discord and self.network) or not (self.discord or self.network):
			raise ValidationError("You must specify either a server OR a network.")
			
class Report(models.Model): # Subject to change
	reporter = models.CharField(max_length=50)
	reportee = models.CharField(max_length=50)
	reason = models.CharField(max_length=256)
	datetime = models.DateTimeField(auto_now_add=True)
	