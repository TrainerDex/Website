import os
from django.db import models
from django.contrib.auth.models import User
from colorful.fields import RGBColorField

def factionImagePath(instance, filename):
	return os.path.join('media/factionLogo', filename)

def leaderImagePath(instance, filename):
	return os.path.join('media/factionLeader', filename)

class Trainer(models.Model):
	username = models.CharField(max_length=30, unique=True)
	start_date = models.DateField(null=True, blank=True)
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, null=True)
	join_date = models.DateField(auto_now_add=True)
	has_cheated = models.BooleanField(default=False)
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False)
	statistics = models.BooleanField(default=True)
	daily_goal = models.IntegerField(null=True, blank=True)
	total_goal = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	prefered = models.BooleanField(default=True)
	#Third Party Accounts
	discord = models.ForeignKey('Discord_User', on_delete=models.SET_NULL, null=True, blank=True)
	ekpogo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	
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

class Trainer_Level(models.Model):
	level = models.AutoField(primary_key=True)
	min_total_xp = models.IntegerField(blank=True, null=False)
	relative_xp = models.IntegerField()
	
	def __str__(self):
		return "Level"+str(self.level)

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

class Discord_User(models.Model):
	account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	name = models.CharField(max_length=32)
	id = models.CharField(max_length=256, primary_key=True)
	discriminator = models.CharField(max_length=256)
	avatar_url = models.URLField()
	creation = models.DateTimeField()
	
	def __str__(self):
		return self.name

class Discord_Server(models.Model):
	name = models.CharField(max_length=256)
	region = models.CharField(max_length=256)
	id = models.CharField(max_length=256, primary_key=True)
	icon = models.CharField(max_length=256)
	owner = models.ForeignKey('Discord_User', on_delete=models.SET_NULL, null=True, blank=True)
	bans_cheaters = models.BooleanField(default=True)
	seg_cheaters = models.BooleanField(default=False)
	bans_minors = models.BooleanField(default=False)
	seg_minors = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

class Discord_Relation(models.Model):
	user = models.ForeignKey('Discord_User', on_delete=models.CASCADE)
	server = models.ForeignKey('Discord_Server', on_delete=models.CASCADE)
	verified = models.BooleanField(default=False)
	ban = models.BooleanField(default=False)
	
	def __str__(self):
		return str(self.user)+' '+str(self.server)
