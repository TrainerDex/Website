# -*- coding: utf-8 -*-
from datetime import date
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import *
from colorful.fields import RGBColorField

def factionImagePath(instance, filename):
	return 'factions/'+instance.name

def leaderImagePath(instance, filename):
	return 'factions/'+instance.name+'-leader'

class ExtendedProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='extended_profile')
	dob = models.DateField(null=True, blank=True, verbose_name="date of birth")
	
	def __str__(self):
		return self.user.username
	
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			ExtendedProfile.objects.create(user=instance)
			
	post_save.connect(create_user_profile, sender=User)

class Trainer(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
	username = models.CharField(max_length=30, unique=True)
	start_date = models.DateField(null=True, blank=True)
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, null=True, verbose_name="team")
	has_cheated = models.BooleanField(default=False, verbose_name="known to have spoofed")
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False, verbose_name="known spoofer")
	statistics = models.BooleanField(default=True)
	daily_goal = models.PositiveIntegerField(null=True, blank=True)
	total_goal = models.PositiveIntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	prefered = models.BooleanField(default=True, verbose_name="main profile")
	go_fest_2017 = models.BooleanField(default=False, verbose_name="Pokémon GO Fest Chicago")
	outbreak_2017 = models.BooleanField(default=False, verbose_name="Pikachu Outbreak 2017")
	safari_zone_2017_oberhausen = models.BooleanField(default=False, verbose_name="Safari Zone - Oberhausen, Germany")
	safari_zone_2017_paris = models.BooleanField(default=False, verbose_name="Safari Zone - Paris, France")
	safari_zone_2017_barcelona = models.BooleanField(default=False, verbose_name="Safari Zone - Barcelona, Spain")
	safari_zone_2017_copenhagen = models.BooleanField(default=False, verbose_name="Safari Zone - Copenhagen, Denmark")
	safari_zone_2017_prague = models.BooleanField(default=False, verbose_name="Safari Zone - Prague, Czechia")
	safari_zone_2017_stockholm = models.BooleanField(default=False, verbose_name="Safari Zone - Stockholm, Sweden")
	safari_zone_2017_amstelveen = models.BooleanField(default=False, verbose_name="Safari Zone - Amstelveen, The Netherlands")
	#top_50 = models.TextField(null=True, blank=True)
	
	def __str__(self):
		return self.username
	
	class Meta:
		ordering = ['username']

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
	datetime = models.DateTimeField(default=timezone.now)
	xp = models.PositiveIntegerField(verbose_name='Total XP')
	dex_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name="seen")
	dex_seen = models.PositiveIntegerField(null=True, blank=True, verbose_name="caught")
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name="jogger")
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name="kanto")
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name="collector")
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name="scientist")
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name="backpacker")
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name="battle girl")
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name="johto")
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name="berry master")
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name="gym leader")
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name="breeder")
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name="fisherman")
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name="ace trainer")
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name="youngster")
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name="pikachu fan")
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name="unown")
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name="champion")
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name="battle legend")
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name="hoenn")
	#Pokemon-demographics
	pkmn_normal = models.PositiveIntegerField(null=True, blank=True, verbose_name="schoolkid")
	pkmn_flying = models.PositiveIntegerField(null=True, blank=True, verbose_name="bird keeper")
	pkmn_poison = models.PositiveIntegerField(null=True, blank=True, verbose_name="punk girl")
	pkmn_ground = models.PositiveIntegerField(null=True, blank=True, verbose_name="ruin maniac")
	pkmn_rock = models.PositiveIntegerField(null=True, blank=True, verbose_name="hiker")
	pkmn_bug = models.PositiveIntegerField(null=True, blank=True, verbose_name="bug catcher")
	pkmn_steel = models.PositiveIntegerField(null=True, blank=True, verbose_name="depot agent")
	pkmn_fire = models.PositiveIntegerField(null=True, blank=True, verbose_name="kindler")
	pkmn_water = models.PositiveIntegerField(null=True, blank=True, verbose_name="swimmer")
	pkmn_grass = models.PositiveIntegerField(null=True, blank=True, verbose_name="gardener")
	pkmn_electric = models.PositiveIntegerField(null=True, blank=True, verbose_name="rocker")
	pkmn_psychic = models.PositiveIntegerField(null=True, blank=True, verbose_name="psychic")
	pkmn_dark = models.PositiveIntegerField(null=True, blank=True, verbose_name="delinquent")
	pkmn_fairy = models.PositiveIntegerField(null=True, blank=True, verbose_name="fairy tale girl")
	pkmn_fighting = models.PositiveIntegerField(null=True, blank=True, verbose_name="black belt")
	pkmn_ghost = models.PositiveIntegerField(null=True, blank=True, verbose_name="hex maniac")
	pkmn_ice = models.PositiveIntegerField(null=True, blank=True, verbose_name="skier")
	pkmn_dragon = models.PositiveIntegerField(null=True, blank=True, verbose_name="dragon tamer")
	#Badges
	gym_badges = models.PositiveIntegerField(null=True, blank=True)
	
	def __str__(self):
		return self.trainer.username+' '+str(self.xp)+' '+str(self.datetime)
	
	class Meta:
		get_latest_by = 'datetime'
		ordering = ['-datetime']

class DiscordUser(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='discord_account')
	name = models.CharField(max_length=32)
	discriminator = models.CharField(max_length=4, blank=False)
	id = models.CharField(max_length=20, primary_key=True, verbose_name="ID")
	avatar_url = models.URLField(null=True, blank=True)
	creation = models.DateTimeField()
	
	def __str__(self):
		return self.name+'#'+str(self.discriminator)
	
	class Meta:
		ordering = ['name']

class DiscordServer(models.Model):
	name = models.CharField(max_length=256)
	region = models.CharField(max_length=256)
	id = models.CharField(max_length=256, primary_key=True, verbose_name="ID")
	icon = models.CharField(max_length=256, null=True, blank=True)
	owner = models.ForeignKey('DiscordUser', on_delete=models.SET_NULL, null=True, blank=True)
	members = models.ManyToManyField('DiscordUser', through='DiscordMember', related_name='discord_members')
	bans_cheaters = models.BooleanField(default=True)
	seg_cheaters = models.BooleanField(default=False, verbose_name="segregates cheaters")
	bans_minors = models.BooleanField(default=False)
	seg_minors = models.BooleanField(default=False, verbose_name="segregates minors")
	
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
