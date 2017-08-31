from django.db import models

def factionImagePath(instance, filename):
	return os.path.join('factionLogo', str(instance.id), filename)

def leaderImagePath(instance, filename):
	return os.path.join('factionLeader', str(instance.id), filename)


#Login Models

class Directory_Users(models.Model):
	email = models.EmailField()
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=50)

class Trainer(models.Model):
	account = models.ForeignKey('Directory_Users', on_delete=models.SET_NULL, null=True, blank=True)
	username = models.CharField(max_length=30, unique=True)
	discord = models.ForeignKey('Discord_Users', on_delete=models.SET_NULL, null=True, blank=True) 
	start_date = models.DateField(null=True, blank=True)
	faction = models.ForeignKey('Factions', on_delete=models.SET_DEFAULT, default=0)
	join_date = models.DateField(auto_now_add=True)
	has_cheated = models.BooleanField(default=False)
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False)
	statistics = models.BooleanField(default=True)
	daily_goal = models.IntegerField(null=True, blank=True)
	total_goal = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)

class Factions(models.Model):
	faction_name = models.CharField(max_length=140)
	faction_colour = models.IntegerField(null=True, blank=True)
	faction_image = models.ImageField(upload_to=factionImagePath, blank=True, null=True)
	leader_name = models.CharField(max_length=140, null=True, blank=True)
	leader_image = models.ImageField(upload_to=leaderImagePath, blank=True, null=True)

class Trainer_Levels(models.Model):
	level = models.AutoField(primary_key=True)
	min_total_xp = models.IntegerField(blank=True, null=False)
	relative_xp = models.IntegerField()

class Experience(models.Model):
	trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	xp = models.IntegerField(verbose_name='Total XP')
	dex_caught = models.IntegerField(null=True, blank=True)
	dex_seen = models.IntegerField(null=True, blank=True)
	walk_dist = models.IntegerField(null=True, blank=True)
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

class Discord_Users(models.Model):
	account = models.ForeignKey('Directory_Users', on_delete=models.SET_NULL, null=True, blank=True)
	d_name = models.CharField(max_length=32)
	d_id = models.CharField(max_length=256, primary_key=True)
	d_discriminator = models.CharField(max_length=256)
	d_avatar_url = models.URLField()
	d_creation = models.DateTimeField()
	dob = models.DateField(null=True, blank=True)
	real_name = models.CharField(max_length=256, null=True, blank=True)

class Discord_Servers(models.Model):
	s_name = models.CharField(max_length=256)
	s_region = models.CharField(max_length=256)
	s_id = models.CharField(max_length=256, primary_key=True)
	s_icon = models.CharField(max_length=256)
	s_owner = models.ForeignKey('Discord_Users', on_delete=models.SET_NULL, null=True, blank=True)
	bans_cheaters = models.BooleanField(default=True)
	seg_cheaters = models.BooleanField(default=False)
	bans_minors = models.BooleanField(default=False)
	seg_minors = models.BooleanField(default=False)

class Discord_Relations(models.Model):
	d_id = models.ForeignKey('Discord_Users', on_delete=models.CASCADE)
	d_server = models.ForeignKey('Discord_Servers', on_delete=models.CASCADE)
	verified = models.BooleanField(default=False)
	ban = models.BooleanField(default=False)
