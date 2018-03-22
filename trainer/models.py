# -*- coding: utf-8 -*-
import uuid
from os.path import splitext
from cities.models import Country, Region, Subregion, City, District
from colorful.fields import RGBColorField
from datetime import date, datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop as _noop
from trainer.validators import *

def factionImagePath(instance, filename):
	return 'img/'+instance.name #remains for legacy reasons

def leaderImagePath(instance, filename):
	return 'img/'+instance.name+'-leader' #remains for legacy reasons

def VerificationImagePath(instance, filename):
	return 'v_{0}_{1}{ext}'.format(instance.owner.id, datetime.utcnow().timestamp(), ext=splitext(filename)[1])

def VerificationUpdateImagePath(instance, filename):
	return 'v_{0}/v_{1}_{2}{ext}'.format(instance.trainer.owner.id, instance.trainer.id, instance.meta_time_created.timestamp(), ext=splitext(filename)[1])

class Trainer(models.Model):
	owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer', verbose_name=_("User"))
	username = CICharField(max_length=30, unique=True, validators=[PokemonGoUsernameValidator], verbose_name=_("Username")) #CaseInsensitive
	start_date = models.DateField(null=True, blank=True, validators=[StartDateValidator], verbose_name=_("Start Date"))
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, verbose_name=_("Team"))
	has_cheated = models.BooleanField(default=False, verbose_name=_("Historic Cheater"))
	last_cheated = models.DateField(null=True, blank=True, verbose_name=_("Last Cheated"))
	currently_cheats = models.BooleanField(default=False, verbose_name=_("Cheater"))
	statistics = models.BooleanField(default=True, verbose_name=_("Statistics"))
	daily_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rate Goal"))
	total_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Reach Goal"))
	last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last Modified"))
	
	go_fest_2017 = models.BooleanField(default=False, verbose_name=_("Pokémon GO Fest Chicago"))
	outbreak_2017 = models.BooleanField(default=False, verbose_name=_("Pikachu Outbreak 2017"))
	safari_zone_2017_oberhausen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Oberhausen, Germany")
	safari_zone_2017_paris = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Paris, France")
	safari_zone_2017_barcelona = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Barcelona, Spain")
	safari_zone_2017_copenhagen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Copenhagen, Denmark")
	safari_zone_2017_prague = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Prague, Czechia")
	safari_zone_2017_stockholm = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Stockholm, Sweden")
	safari_zone_2017_amstelveen = models.BooleanField(default=False, verbose_name=_("Safari Zone")+" - Amstelveen, The Netherlands")
	
	leaderboard_country = models.ForeignKey(Country, null=True, blank=True, verbose_name=_("Country"), related_name='leaderboard_trainers_country')
	leaderboard_region = models.ForeignKey(Region, null=True, blank=True, verbose_name=_("Region"), related_name='leaderboard_trainers_region')
	leaderboard_subregion = models.ForeignKey(Subregion, null=True, blank=True, verbose_name=_("Subregion"), related_name='leaderboard_trainers_subregion')
	leaderboard_city = models.ForeignKey(City, null=True, blank=True, verbose_name=_("City"), related_name='leaderboard_trainers_city')
	
	verified = models.BooleanField(default=False, verbose_name=_("Verified"))
	
	event_10b = models.BooleanField(default=False)
	event_1k_users = models.BooleanField(default=False)
	
	verification = models.ImageField(upload_to=VerificationImagePath, null=True, blank=True)
	
	def is_prefered(self):
		return True if owner.prefered_profile == self else False
	
	def __str__(self):
		return self.username
	
	@property
	def active(self):
		return self.owner.active
	
	@property
	def profile_complete(self):
		return bool(
			bool(self.owner) and bool(self.username) and bool(self.verification)
		)
	
	@property
	def profile_completed_optional(self):
		return bool(
			bool(self.profile_complete) and
			bool(self.start_date)
		)
	
	def clean(self):
		if (self.has_cheated is True or self.currently_cheats is True) and self.last_cheated is None:
			self.has_cheated = True
			self.last_cheated = date.today()
		elif self.currently_cheats is True:
			self.has_cheated = True
	
	def get_absolute_url(self):
		return reverse('profile', kwargs={'id':self.pk})
	
	class Meta:
		ordering = ['username']
		verbose_name = _("Trainer")
		verbose_name_plural = _("Trainers")

@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
	if kwargs['created']:
		trainer = Trainer.objects.create(owner=kwargs['instance'], username=kwargs['instance'].username)
		return trainer
	return None

class Faction(models.Model):
	name = models.CharField(max_length=140, verbose_name=_("Name"))
	colour = RGBColorField(default='#929292', null=True, blank=True, verbose_name=_("Colour"))
	leader_name = models.CharField(max_length=140, null=True, blank=True, verbose_name=_("Leader"))
	
	@property
	def image(self):
		return 'img/'+self.name+'.png'
	
	@property
	def vector_image(self):
		return 'img/'+self.name+'.svg'
	
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
	
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name=_("Jogger"))
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Kanto"))
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Collector"))
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Scientist"))
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Breeder"))
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Backpacker"))
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Battle Girl"))
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fisherman"))
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ace Trainer"))
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Youngster"))
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pikachu Fan"))
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Johto"))
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Unown"))
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Berry Master"))
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Gym Leader"))
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Champion"))
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Battle Legend"))
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Hoenn"))
	quests = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pokémon Ranger"))
	mew_encountered = models.PositiveIntegerField(null=True, blank=True, verbose_name=_noop("Mew"))
	
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
	DATABASE_SOURCES = ( #cs crowd sourced # ts text sourced # ss screenshot
		('?', _noop('undefined')),
		('cs_social_twitter', _noop('Twitter (Found)')),
		('cs_social_facebook', _noop('Facebook (Found)')),
		('cs_social_youtube', _noop('YouTube (Found)')),
		('cs_?', _noop('Sourced Elsewhere')),
		('ts_social_discord', _noop('Discord')),
		('ts_social_twitter', _noop('Twitter')),
		('ts_direct', _noop('Directly told (via text)')),
		('web_quick', _noop('Quick Update (Web)')),
		('web_detailed', _noop('Detailed Update (Web)')),
		('ts_registration', _noop('Registration')),
		('ss_registration', _noop('Registration w/ Screenshot')),
		('ss_generic', _noop('Generic Screenshot')),
		('ss_ocr', _noop("OCR Screenshot")),
	)
	meta_source = models.CharField(max_length=256, choices=DATABASE_SOURCES, default='?', verbose_name=_("Source"))
	
	image_proof = models.ImageField(upload_to=VerificationUpdateImagePath, null=True, blank=True)
	
	def meta_crowd_sourced(self):
		if self.meta_source.startswith('cs'):
			return True
		return False
	meta_crowd_sourced.boolean = True
	meta_crowd_sourced.short_description = _("Crowd Sourced")
	
	
	def __str__(self):
		return self.trainer.username+' '+str(self.xp)+' '+str(self.update_time)
	
	def clean(self):
		
		error_dict = {}
		try: # Workaround for inital registrations
			for field in Update._meta.get_fields():
				if type(field) == models.PositiveIntegerField or field.name == 'walk_dist':
					largest = Update.objects.filter(trainer=self.trainer, update_time__lt=self.update_time).exclude(**{field.name : None}).order_by('-'+field.name).first() # Gets updates, filters by same trainer, excludes updates where that field is empty, get update with highest value in that field - this should always be the correct update
					if largest is not None and getattr(self, field.name) is not None and getattr(self, field.name) < getattr(largest, field.name):
						error_dict[field.name] = ValidationError(_("This value has previously been entered at a higher value. Please try again, ensuring you enter your Total XP."))
		except Exception as e:
			if str(e) != 'Update has no trainer.':
				raise e
		
		if self.update_time.date() < date(2017,6,20):
			self.raids_completed = None
			self.leg_raids_completed = None
			self.berry_fed = None
			self.gym_defended = None
		
		if self.update_time.date() >= date(2017,6,20):
			self.legacy_gym_trained = None
		
		if self.update_time.date() < date(201,3,30):
			self.quests = None
			self.mew_encountered = None
		
		if self.update_time.date() < date(2017,10,20):
			self.gen_3_dex = None
		
		if self.update_time.date() < date(2016,12,1):
			self.gen_2_dex = None
			self.unown_alphabet = None
		
		if error_dict != {}:
			raise ValidationError(error_dict)
	
	def get_absolute_url(self):
		return reverse('update_detail', kwargs={'uuid':self.uuid})
	
	class Meta:
		get_latest_by = 'update_time'
		ordering = ['-update_time']
		verbose_name = _("Update")
		verbose_name_plural = _("Updates")
	

class TrainerReport(models.Model):
	trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name=_("Trainer"))
	reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Reported by"))
	report = models.TextField(verbose_name=_("Report"))
	
	class Meta:
		verbose_name=_("Report")
		verbose_name_plural=_("Reports")
