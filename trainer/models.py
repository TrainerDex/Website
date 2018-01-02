import uuid
from colorful.fields import RGBColorField
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import *
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from exclusivebooleanfield.fields import ExclusiveBooleanField
from trainer.validators import *

def factionImagePath(instance, filename):
	return 'factions/'+instance.name

def leaderImagePath(instance, filename):
	return 'factions/'+instance.name+'-leader'

class Trainer(models.Model):
	owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
	active = models.BooleanField(default=True)
	username = models.CharField(max_length=30, unique=True)
	start_date = models.DateField(null=True, blank=True, validators=[validate_startdate])
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, verbose_name=_("team"))
	has_cheated = models.BooleanField(default=False, verbose_name=_("known to have spoofed"))
	last_cheated = models.DateField(null=True, blank=True)
	currently_cheats = models.BooleanField(default=False, verbose_name=_("known spoofer"))
	statistics = models.BooleanField(default=True)
	daily_goal = models.PositiveIntegerField(null=True, blank=True)
	total_goal = models.PositiveIntegerField(null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	go_fest_2017 = models.BooleanField(default=False, verbose_name=_("Pokémon GO Fest Chicago"))
	outbreak_2017 = models.BooleanField(default=False, verbose_name=_("Pikachu Outbreak 2017"))
	safari_zone_2017_oberhausen = models.BooleanField(default=False, verbose_name=_("Safari Zone - Oberhausen, Germany"))
	safari_zone_2017_paris = models.BooleanField(default=False, verbose_name=_("Safari Zone - Paris, France"))
	safari_zone_2017_barcelona = models.BooleanField(default=False, verbose_name=_("Safari Zone - Barcelona, Spain"))
	safari_zone_2017_copenhagen = models.BooleanField(default=False, verbose_name=_("Safari Zone - Copenhagen, Denmark"))
	safari_zone_2017_prague = models.BooleanField(default=False, verbose_name=_("Safari Zone - Prague, Czechia"))
	safari_zone_2017_stockholm = models.BooleanField(default=False, verbose_name=_("Safari Zone - Stockholm, Sweden"))
	safari_zone_2017_amstelveen = models.BooleanField(default=False, verbose_name=_("Safari Zone - Amstelveen, The Netherlands"))
	prefered = ExclusiveBooleanField(on='owner')
	#top_50 = models.TextField(null=True, blank=True)
	
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
	uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
	trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE)
	update_time = models.DateTimeField(default=timezone.now)
	xp = models.PositiveIntegerField(verbose_name='Total XP')
	dex_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("caught"))
	dex_seen = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("seen"))
	gym_badges = models.PositiveIntegerField(null=True, blank=True)
	
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name=_("jogger"))
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("kanto"))
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("collector"))
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("scientist"))
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("breeder"))
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("backpacker"))
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("fisherman"))
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("battle girl"))
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("ace trainer"))
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("youngster"))
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("pikachu fan"))
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("johto"))
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("unown"))
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("berry master"))
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("gym leader"))
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("champion"))
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("battle legend"))
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("hoenn"))
	
	pkmn_normal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("schoolkid"))
	pkmn_flying = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("bird keeper"))
	pkmn_poison = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("punk girl"))
	pkmn_ground = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("ruin maniac"))
	pkmn_rock = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("hiker"))
	pkmn_bug = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("bug catcher"))
	pkmn_steel = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("depot agent"))
	pkmn_fire = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("kindler"))
	pkmn_water = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("swimmer"))
	pkmn_grass = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("gardener"))
	pkmn_electric = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("rocker"))
	pkmn_psychic = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("psychic"))
	pkmn_dark = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("delinquent"))
	pkmn_fairy = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("fairy tale girl"))
	pkmn_fighting = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("black belt"))
	pkmn_ghost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("hex maniac"))
	pkmn_ice = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("skier"))
	pkmn_dragon = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("dragon tamer"))
	
	meta_time_created = models.DateTimeField(auto_now_add=True)
	
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
