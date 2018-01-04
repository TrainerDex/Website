﻿import uuid
from colorful.fields import RGBColorField
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import *
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from exclusivebooleanfield.fields import ExclusiveBooleanField
from trainer.validators import *

def factionImagePath(instance, filename):
	return 'factions/'+instance.name

def leaderImagePath(instance, filename):
	return 'factions/'+instance.name+'-leader'

class Trainer(models.Model):
	owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles', verbose_name=_("User"))
	active = models.BooleanField(default=True, verbose_name=_("Active"))
	username = models.CharField(max_length=30, unique=True, verbose_name=_("Username"))
	start_date = models.DateField(null=True, blank=True, validators=[validate_startdate], verbose_name=_("Start Date"))
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, verbose_name=_("Team"))
	has_cheated = models.BooleanField(default=False, verbose_name=_("Historic Cheater"))
	last_cheated = models.DateField(null=True, blank=True, verbose_name=_("Last Cheated"))
	currently_cheats = models.BooleanField(default=False, verbose_name=_("Cheater"))
	statistics = models.BooleanField(default=True, verbose_name=_("Statistics"))
	daily_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rate Goal"))
	total_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Reach Goal"))
	last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last Modified"))
	go_fest_2017 = models.BooleanField(default=False, verbose_name=_("Pokémon GO Fest Chicago"))
	outbreak_2017 = models.BooleanField(default=False, verbose_name=_("Pikachu Outbreak")+" 2017")
	safari_zone_2017_oberhausen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Oberhausen, Germany"))
	safari_zone_2017_paris = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Paris, France"))
	safari_zone_2017_barcelona = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Barcelona, Spain"))
	safari_zone_2017_copenhagen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Copenhagen, Denmark"))
	safari_zone_2017_prague = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Prague, Czechia"))
	safari_zone_2017_stockholm = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Stockholm, Sweden"))
	safari_zone_2017_amstelveen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - "+("Amstelveen, The Netherlands"))
	prefered = ExclusiveBooleanField(on='owner')
	
	def is_prefered(self):
		return True if owner.prefered_profile == self else False
	
	def __str__(self):
		return self.username
	
	def clean(self):
		if (self.has_cheated is True or self.currently_cheats is True) and self.last_cheated is None:
			self.has_cheated = True
			self.last_cheated = date.today()
		elif self.currently_cheats is True:
			self.has_cheated = True
	
	def get_absolute_url(self):
		return reverse('profile_short', args=[self.username])
	
	class Meta:
		ordering = ['username']
		verbose_name = _("Trainer")
		verbose_name_plural = _("Trainers")

class Faction(models.Model):
	name = models.CharField(max_length=140, verbose_name=_("Name"))
	colour = RGBColorField(default='#929292', null=True, blank=True, verbose_name=_("Colour"))
	image = models.ImageField(upload_to=factionImagePath, blank=True, null=True, verbose_name=_("Image"))
	leader_name = models.CharField(max_length=140, null=True, blank=True, verbose_name=_("Leader"))
	leader_image = models.ImageField(upload_to=leaderImagePath, blank=True, null=True, verbose_name="{} ({})".format(_("Leader"),_("Image")))
	
	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name = _("Team")
		verbose_name_plural = _("Teams")

class Update(models.Model):
	uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name="UUID")
	trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, verbose_name=_("Trainer"))
	update_time = models.DateTimeField(default=timezone.now, verbose_name=_("Time Updated"))
	xp = models.PositiveIntegerField(verbose_name=_("XP"))
	dex_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Species Caught"))
	dex_seen = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Species Seen"))
	gym_badges = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Total Gym Badges"))
	
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name=_("Distance Walked"))
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Kanto Pokédex"))
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pokémon Caught"))
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pokémon Evolved"))
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Eggs Hatched"))
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pokéstops Spun"))
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Big Magikarp"))
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Battles Won"))
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ace Trainer"))
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Tiny Rattata"))
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pikachu Caught"))
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Johto Pokédex"))
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Unown"))
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Berries Fed"))
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Gyms Defended (Hours)"))
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Raids Completed (Levels 1-4)"))
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Raids Completed (Level 5)"))
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Hoenn Pokédex"))
	
	pkmn_normal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Normal"))
	pkmn_flying = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Flying"))
	pkmn_poison = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Poison"))
	pkmn_ground = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ground"))
	pkmn_rock = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rock"))
	pkmn_bug = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Bug"))
	pkmn_steel = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Steel"))
	pkmn_fire = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fire"))
	pkmn_water = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Water"))
	pkmn_grass = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Grass"))
	pkmn_electric = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Electric"))
	pkmn_psychic = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pychic"))
	pkmn_dark = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Dark"))
	pkmn_fairy = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fary"))
	pkmn_fighting = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fighting"))
	pkmn_ghost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ghost"))
	pkmn_ice = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ice"))
	pkmn_dragon = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Dragon"))
	
	meta_time_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Time Created"))
	
	def __str__(self):
		return self.trainer.username+' '+str(self.xp)+' '+str(self.update_time)
	
	def clean(self):
		
		error_dict = {}
		
		for field in Update._meta.get_fields():
			if type(field) == models.PositiveIntegerField or field.name == 'walk_dist':
				largest = Update.objects.filter(trainer=self.trainer, update_time__lt=self.update_time).exclude(**{field.name : None}).order_by('-'+field.name).first() # Gets updates, filters by same trainer, excludes updates where that field is empty, get update with highest value in that field - this should always be the correct update
				if largest is not None and getattr(self, field.name) is not None and getattr(self, field.name) < getattr(largest, field.name):
					error_dict[field.name] = ValidationError(_("This value has previously been entered at a higher value. Please try again, ensuring you enter your Total XP."))
		
		if self.update_time.date() < date(2017,6,20):
			self.raids_completed = None
			self.leg_raids_completed = None
			self.berry_fed = None
			self.gym_defended = None
		
		if self.update_time.date() >= date(2017,6,20):
			self.legacy_gym_trained = None
		
		if self.update_time.date() < date(2017,10,20):
			self.gen_3_dex = None
		
		if self.update_time.date() < date(2016,12,1):
			self.gen_2_dex = None
			self.unown_alphabet = None
		
		if error_dict != {}:
			raise ValidationError(error_dict)
	
	class Meta:
		get_latest_by = 'update_time'
		ordering = ['-update_time']
		verbose_name = _("Update")
		verbose_name_plural = _("Updates")
