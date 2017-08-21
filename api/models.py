import uuid
from django.db import models

# Create your models here.

def factionImagePath(instance, filename):
	return os.path.join('factions', str(instance.id), filename)

class Factions(models.Model):
	faction_name = models.CharField(max_length=140)
	faction_colour = models.IntegerField(null=True, blank=True)
#	faction_image = models.ImageField(upload_to=factionImagePath, blank=True, null=True)
	leader_name = models.CharField(max_length=140, null=True, blank=True)
#	leader_image = models.ImageField(upload_to=leaderImagePath, blank=True, null=True) #https://stackoverflow.com/questions/8189800/django-store-user-image-in-model

def __str__(self):
	return '{}'.format(self.faction_name)

class Trainer_Levels(models.Model):
	level = models.AutoField(primary_key=True)
	min_total_xp = models.IntegerField(blank=True, null=False)
	relative_xp = models.IntegerField()
	
class Trainers(models.Model):
	username = models.CharField(max_length=30, unique=True)
	discord = models.ForeignKey('Discordian', on_delete=models.CASCADE)
	start_date = models.DateField(null=True, blank=True)
	join_date = models.DateField(auto_now_add=True)
	has_cheated = models.BooleanField(default=False)
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False)
	statistics = models.BooleanField(default=True)
	daily_goal = models.IntegerField(null=True, blank=True)
	total_goal = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	
class Experience(models.Model):
	trainer = models.ForeignKey('Trainers', on_delete=models.CASCADE, to_field='username')
	xp = models.IntegerField(verbose_name='Total XP')
	datetime = models.DateTimeField(auto_now_add=True)
	
class Discordian(models.Model):
	d_name = models.CharField(max_length=32)
	d_id = models.CharField(max_length=256, primary_key=True)
	d_discriminator = models.CharField(max_length=256)
	d_avatar_url = models.URLField()
	d_creation = models.DateTimeField()
	dob = models.DateField(null=True, blank=True)
	real_name = models.CharField(max_length=256, null=True, blank=True)
	
class Servers(models.Model):
	s_name = models.CharField(max_length=256)
	s_region = models.CharField(max_length=256)
	s_id = models.CharField(max_length=256, primary_key=True)
	s_icon = models.CharField(max_length=256)
	s_owner = models.ForeignKey('Discordian', on_delete=models.CASCADE)
	bans_cheaters = models.BooleanField(default=True)
	seg_cheaters = models.BooleanField(default=False)
	bans_minors = models.BooleanField(default=False)
	seg_minors = models.BooleanField(default=False)
	
class Discordian_On_Servers(models.Model):
	d_id = models.ForeignKey('Discordian', on_delete=models.CASCADE)
	d_server = models.ForeignKey('Servers', on_delete=models.CASCADE)
	verified = models.BooleanField(default=False)
	ban = models.BooleanField(default=False)
	