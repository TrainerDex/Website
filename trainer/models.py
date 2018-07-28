﻿# -*- coding: utf-8 -*-
import uuid
from os.path import splitext
from cities.models import Country, Region
from colorful.fields import RGBColorField
from datetime import date, datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop as _noop
from trainer.validators import *
from trainer.shortcuts import level_parser, int_to_unicode, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, lookup

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
	username = postgres_fields.CICharField(max_length=15, unique=True, validators=[PokemonGoUsernameValidator], verbose_name=_("Nickname"), help_text=_("Your Trainer Nickname exactly as is in game. You are free to change capitalisation but removal or addition of digits may prevent other Trainers with similar usernames from using this service and is against the Terms of Service."))
	start_date = models.DateField(null=True, blank=True, validators=[StartDateValidator], verbose_name=_("Start Date"), help_text=_("The date you created your Pokémon Go account."))
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, verbose_name=_("Team"), help_text=_("Mystic = Blue, Instinct = Yellow, Valor = Red.") )
	has_cheated = models.BooleanField(default=False, verbose_name=_("Historic Cheater"), help_text=_("Have you cheated in the past?"))
	last_cheated = models.DateField(null=True, blank=True, verbose_name=_("Last Cheated"), help_text=_("When did you last cheat?"))
	currently_cheats = models.BooleanField(default=False, verbose_name=_("Cheater"), help_text=_("Do you still cheat?"))
	statistics = models.BooleanField(default=True, verbose_name=_("Statistics"), help_text=_("Would you like to be shown on the leaderboard? Ticking this box gives us permission to process your data."))
	daily_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rate Goal"), help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP do you aim to gain a day?"))
	total_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Reach Goal"), help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP are you aiming for next?"))
	
	trainer_code = models.CharField(null=True, blank=True, validators=[TrainerCodeValidator], verbose_name=_("Trainer Code"), max_length=15, help_text=_("Fancy sharing your trainer code? (Disclaimer: This information will be public)"))
	
	go_fest_2017 = models.BooleanField(default=False, verbose_name=_("Pokémon GO Fest 2017"), help_text=_("Chicago, July 22, 2017"))
	outbreak_2017 = models.BooleanField(default=False, verbose_name=_("Pokémon GO STADIUM"), help_text=_("Yokohama, August 2017"))
	safari_zone_2017_oberhausen = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Oberhausen, Germany", help_text=_("Europe, September 16, 2017"))
	safari_zone_2017_paris = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Paris, France", help_text=_("Europe, September 16, 2017"))
	safari_zone_2017_barcelona = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Barcelona, Spain", help_text=_("Europe, September 16, 2017"))
	safari_zone_2017_copenhagen = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Copenhagen, Denmark", help_text=_("Europe, October 7, 2017"))
	safari_zone_2017_prague = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Prague, Czechia", help_text=_("Europe, October 7, 2017"))
	safari_zone_2017_stockholm = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Stockholm, Sweden", help_text=_("Europe, October 14, 2017"))
	safari_zone_2017_amstelveen = models.BooleanField(default=False, verbose_name=_("GO Safari Zone - Europe 2017")+" - Amstelveen, The Netherlands", help_text=_("Europe, October 14, 2017"))
	go_fest_2018 = models.BooleanField(default=False, verbose_name=_("Pokémon GO Fest 2018"), help_text=_("Chicago, July 14-15, 2018"))
	special_weekend_2018 = models.BooleanField(default=False, verbose_name="Pokémon GO Special Weekend", help_text=_("Japan, July 26-29, 2018"))
	
	leaderboard_country = models.ForeignKey(Country, null=True, blank=True, verbose_name=_("Country"), related_name='leaderboard_trainers_country', help_text=_("Where are you based?"))
	leaderboard_region = models.ForeignKey(Region, null=True, blank=True, verbose_name=_("Region"), related_name='leaderboard_trainers_region', help_text=_("Where are you based?"))
	
	verified = models.BooleanField(default=False, verbose_name=_("Verified"))
	last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last Modified"))
	
	event_10b = models.BooleanField(default=False)
	event_1k_users = models.BooleanField(default=False)
	
	verification = models.ImageField(upload_to=VerificationImagePath, null=True, blank=True, verbose_name=_("Username / Level / Team Screenshot"))
	
	def is_prefered(self):
		return True
	
	def flag_emoji(self):
		if self.leaderboard_country:
			return lookup(self.leaderboard_country.code)
		else:
			return None
	
	def submitted_picture(self):
		return bool(self.verification)
	submitted_picture.boolean = True
	
	def awaiting_verification(self):
		if bool(self.verification) is True and bool(self.verified) is False:
			return True
		return False
	awaiting_verification.boolean = True
	
	def is_verified(self):
		return self.verified
	is_verified.boolean = True
	
	def is_verified_and_saved(self):
		return bool(bool(self.verified) and bool(self.verification))
	is_verified_and_saved.boolean = True
	
	def is_on_leaderboard(self):
		return bool(self.is_verified and self.statistics)
	is_on_leaderboard.boolean = True
	
	def level(self):
		update = list(self.update_set.all())
		if update:
			update.sort(key=lambda x: x.xp)
			return level_parser(xp=update[-1].xp).level
		return None
	
	def __str__(self):
		return self.username
	
	def circled_level(self):
		level = self.level()
		if level:
			return int_to_unicode(level).strip()
		return None
	
	@property
	def active(self):
		return self.owner.is_active
	
	@property
	def profile_complete(self):
		return bool(
			bool(self.owner) and bool(self.username) and bool(bool(self.verification) or bool(self.verified))
		)
	
	@property
	def profile_completed_optional(self):
		return bool(
			bool(self.profile_complete) and
			bool(self.start_date)
		)
	
	def clean(self):
		# Cleanup functions
		
		# Cheating values
		if (self.has_cheated is True or self.currently_cheats is True) and self.last_cheated is None:
			self.has_cheated = True
			self.last_cheated = date.today()
		elif self.currently_cheats is True:
			self.has_cheated = True
		
		# Leaderboard preference
		if self.leaderboard_region and (self.leaderboard_region.country != self.leaderboard_country):
			self.leaderboard_region = None
	
	def get_absolute_url(self):
		return reverse('profile_username', kwargs={'username':self.username})
	
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
	xp = models.PositiveIntegerField(verbose_name=_("XP"), help_text=_("Your Total XP can be found at the bottom of your Pokémon Go profile"))
	dex_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Species Caught"), help_text=_("In your Pokédex, how many differnt species have you caught? It should say at the top."))
	dex_seen = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Species Seen"), help_text=_("In your Pokédex, how many differnt species have you seen? It should say at the top."))
	gym_badges = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Total Gym Badges"), help_text=_("Your gym badges map. Total number of gold, silver, bronze and blank combined. (This information is currently not used)"))
	
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name=_("Jogger"), help_text=_("Walk 1,000km"))
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Kanto"), help_text=_("Register 100 Kanto region Pokémon in the Pokédex."))
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Collector"), help_text=_("Catch 2,000 Pokémon."))
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Scientist"), help_text=_("Evolve 200 Pokémon."))
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Breeder"), help_text=_("Hatch 500 eggs."))
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Backpacker"), help_text=_("Visit 2,000 PokéStops."))
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Battle Girl"), help_text=_("Win 1,000 Gym battles."))
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fisherman"), help_text=_("Catch 300 big Magikarp."))
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ace Trainer"), help_text=_("Train 1,000 times."))
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Youngster"), help_text=_("Catch 300 tiny Rattata."))
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pikachu Fan"), help_text=_("Catch 300 Pikachu."))
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Johto"), help_text=_("Register 70 Pokémon first discovered in the Johto region to the Pokédex."))
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Unown"), help_text=_("Catch 26 Unown."))
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Berry Master"), help_text=_("Feed 1,000 Berries at Gyms."))
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Gym Leader"), help_text=_("Defend Gyms for 1,000 hours."))
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Champion"), help_text=_("Win 1,000 Raids."))
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Battle Legend"), help_text=_("Win 1,000 Legendary Raids."))
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Hoenn"), help_text=_("Register 70 Pokémon first discovered in the Hoenn region to the Pokédex."))
	quests = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pokémon Ranger"), help_text=_("Complete 1,000 Field Research tasks."))
	max_friends = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Idol"), help_text=_("Become Best Friends with 3 Trainers."))
	trading = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Gentleman"), help_text=_("Trade 1,000 Pokémon."))
	trading_distance = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Pilot"), help_text=_("Earn 1,000,000 km across the distance of all Pokémon trades."))
	
	pkmn_normal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Schoolkid"), help_text=_("Catch 200 Normal-type Pokémon"))
	pkmn_fighting = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Black Belt"), help_text=_("Catch 200 Fighting-type Pokémon"))
	pkmn_flying = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Bird Keeper"), help_text=_("Catch 200 Flying-type Pokémon"))
	pkmn_poison = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Punk Girl"), help_text=_("Catch 200 Poison-type Pokémon"))
	pkmn_ground = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Ruin Maniac"), help_text=_("Catch 200 Ground-type Pokémon"))
	pkmn_rock = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Hiker"), help_text=_("Catch 200 Rock-type Pokémon"))
	pkmn_bug = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Bug Catcher"), help_text=_("Catch 200 Bug-type Pokémon"))
	pkmn_ghost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Hex Maniac"), help_text=_("Catch 200 Ghost-type Pokémon"))
	pkmn_steel = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Depot Agent"), help_text=_("Catch 200 Steel-type Pokémon"))
	pkmn_fire = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Kindler"), help_text=_("Catch 200 Fire-type Pokémon"))
	pkmn_water = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Swimmer"), help_text=_("Catch 200 Water-type Pokémon"))
	pkmn_grass = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Gardener"), help_text=_("Catch 200 Grass-type Pokémon"))
	pkmn_electric = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rocker"), help_text=_("Catch 200 Electric-type Pokémon"))
	pkmn_psychic = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Psychic"), help_text=_("Catch 200 Pychic-type Pokémon"))
	pkmn_ice = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Skier"), help_text=_("Catch 200 Ice-type Pokémon"))
	pkmn_dragon = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Dragon Tamer"), help_text=_("Catch 200 Dragon-type Pokémon"))
	pkmn_dark = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Delinquent"), help_text=_("Catch 200 Dark-type Pokémon"))
	pkmn_fairy = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fairy Tale Girl"), help_text=_("Catch 200 Fairy-type Pokémon"))
	
	meta_time_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Time Created"))
	DATABASE_SOURCES = ( #cs crowd sourced # ts text sourced # ss screenshot
		('?', None),
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
		('com.nianticlabs.pokemongo.friends', _noop("In Game Friends")),
		('com.pokeassistant.trainerstats', "Poké Assistant"),
		('com.pokenavbot.profiles', "PokeNav"),
		('tl40datateam.spreadsheet', "Tl40 Data Team"),
	)
	meta_source = models.CharField(max_length=256, choices=DATABASE_SOURCES, default='?', verbose_name=_("Source"))
	
	image_proof = models.ImageField(upload_to=VerificationUpdateImagePath, null=True, blank=True, verbose_name=_("Total XP Screenshot"))
	
	def meta_crowd_sourced(self):
		if self.meta_source.startswith('cs'):
			return True
		elif self.meta_source == ('?'):
			return None
		return False
	meta_crowd_sourced.boolean = True
	meta_crowd_sourced.short_description = _("Crowd Sourced")
	
	def modified_extra_fields(self):
		return bool([x for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES) if getattr(self, x)])
	modified_extra_fields.boolean = True
	
	def __str__(self):
		return _("{username} - {xp:,}XP at {date}").format(username=self.trainer, xp=self.xp, date=self.update_time.isoformat(sep=' ', timespec='minutes'))
	
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

class DiscordGuild(models.Model):
	id = models.BigIntegerField(primary_key=True)
	cached_data = postgres_fields.JSONField(null=True, blank=True)
	cached_date = models.DateTimeField(auto_now=True)
	
	setting_channels_ocr_enabled = postgres_fields.ArrayField(models.BigIntegerField())
	setting_rename_users = models.BooleanField(default=False)
	
	def __str__(self):
		return str(self.id)
	

class PrivateLeague(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="UUID")
	language = models.CharField(max_length=7, choices=settings.LANGUAGES)
	short_description = models.CharField(max_length=70)
	description = models.TextField(null=True, blank=True)
	vanity = models.SlugField()
	
	privacy_public = models.BooleanField(default=False)
	
	security_ban_sync = models.BooleanField(default=False)
	security_kick_sync = models.BooleanField(default=False)
	
	memberships_personal = models.ManyToManyField(
		Trainer,
		through='PrivateLeagueMembershipPersonal',
		through_fields=('league', 'trainer')
	)
	memberships_discord = models.ManyToManyField(
		DiscordGuild,
		through='PrivateLeagueMembershipDiscord',
		through_fields=('league', 'discord')
	)
	
	def __str__(self):
		return self.short_description

class PrivateLeagueMembershipPersonal(models.Model):
	league = models.ForeignKey(PrivateLeague, on_delete=models.CASCADE)
	trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
	
	primary = models.BooleanField(default=True)
	
	def __str__(self):
		return "{league} - {trainer}".format(league=self.league, trainer=self.trainer)
	

class PrivateLeagueMembershipDiscord(models.Model):
	league = models.ForeignKey(PrivateLeague, on_delete=models.CASCADE)
	discord = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)
	
	auto_import = models.BooleanField(default=True)
	
	security_ban_sync = models.NullBooleanField()
	security_kick_sync = models.NullBooleanField()
	
	def __str__(self):
		return "{league} - {guild}".format(league=self.league, trainer=self.discord)
	
