# -*- coding: utf-8 -*-
import uuid
import json
import logging
import requests

logger = logging.getLogger('django.trainerdex')

from os.path import splitext
from cities.models import Country, Region
from colorful.fields import RGBColorField
from datetime import date, datetime, timedelta, timezone, time
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.db.models import Max
from django.db.models.signals import *
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop, pgettext_lazy,to_locale, get_supported_language_variant, get_language
from trainer.validators import *
from trainer.shortcuts import level_parser, int_to_unicode, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, UPDATE_SORTABLE_FIELDS, lookup, numbers, UPDATE_NON_REVERSEABLE_FIELDS, BADGES

def factionImagePath(instance, filename):
	return f'img/{instance.slug}'

def leaderImagePath(instance, filename):
	return f'img/{instance.faction.slug}.leader' #remains for legacy reasons

def VerificationImagePath(instance, filename):
	return 'v_{0}_{1}{ext}'.format(instance.owner.id, datetime.utcnow().timestamp(), ext=splitext(filename)[1])

def VerificationUpdateImagePath(instance, filename):
	return 'v_{0}/v_{1}_{2}{ext}'.format(instance.trainer.owner.id, instance.trainer.id, instance.meta_time_created.timestamp(), ext=splitext(filename)[1])

class Trainer(models.Model):
	
	owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer', verbose_name=_("User"))
	username = postgres_fields.CICharField(max_length=15, unique=True, validators=[PokemonGoUsernameValidator], db_index=True, verbose_name=pgettext_lazy("onboard_enter_name_hint", "Nickname"), help_text=_("Your Trainer Nickname exactly as is in game. You are free to change capitalisation but removal or addition of digits may prevent other Trainers with similar usernames from using this service and is against the Terms of Service."))
	start_date = models.DateField(null=True, blank=True, validators=[StartDateValidator], verbose_name=pgettext_lazy("profile_start_date", "Start Date"), help_text=_("The date you created your Pokémon Go account."))
	faction = models.ForeignKey('Faction', on_delete=models.SET_DEFAULT, default=0, verbose_name=_("Team"), help_text=_("Mystic = Blue, Instinct = Yellow, Valor = Red.") )
	last_cheated = models.DateField(null=True, blank=True, verbose_name=_("Last Cheated"), help_text=_("When did this Trainer last cheat?"))
	statistics = models.BooleanField(default=True, verbose_name=pgettext_lazy("Profile_Category_Stats", "Statistics"), help_text=_("Would you like to be shown on the leaderboard? Ticking this box gives us permission to process your data."))
	daily_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rate Goal"), help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP do you aim to gain a day?"))
	total_goal = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Reach Goal"), help_text=_("Our Discord bot lets you know if you've reached you goals or not: How much XP are you aiming for next?"))
	
	trainer_code = models.CharField(null=True, blank=True, validators=[TrainerCodeValidator], verbose_name=pgettext_lazy("friend_code_title", "Trainer Code"), max_length=15, help_text=_("Fancy sharing your trainer code? (Disclaimer: This information will be public)"))
	
	badge_chicago_fest_july_2017 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_chicago_fest_july_2017_title", "Pokémon GO Fest 2017"), help_text=pgettext_lazy("badge_chicago_fest_july_2017", "Chicago, July 22, 2017"))
	badge_pikachu_outbreak_yokohama_2017 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_pikachu_outbreak_yokohama_2017_title", "Pikachu Outbreak 2017"), help_text=pgettext_lazy("badge_pikachu_outbreak_yokohama_2017", "Yokohama, August 2017"))
	badge_safari_zone_europe_2017_09_16 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_safari_zone_europe_2017_title", "GO Safari Zone - Europe 2017"), help_text=pgettext_lazy("badge_safari_zone_europe_2017", "Europe, September 16, 2017"))
	badge_safari_zone_europe_2017_10_07 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_safari_zone_europe_2017_10_07_title", "GO Safari Zone - Europe 2017"), help_text=pgettext_lazy("badge_safari_zone_europe_2017_10_07", "Europe, October 7, 2017"))
	badge_safari_zone_europe_2017_10_14 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_safari_zone_europe_2017_10_14_title", "GO Safari Zone - Europe 2017"), help_text=pgettext_lazy("badge_safari_zone_europe_2017_10_14", "Europe, October 14, 2017"))
	badge_chicago_fest_july_2018 = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_chicago_fest_july_2018_*_*_title", "Pokémon GO Fest 2018"), help_text=pgettext_lazy("badge_chicago_fest_july_2018_*_*", "Chicago, July 14-15, 2018"))
	badge_apac_partner_july_2018_japan = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_apac_partner_july_2018_*_title", "Pokémon GO Special Weekend"), help_text=pgettext_lazy("badge_apac_partner_july_2018_*", "Japan, July 26-29, 2018"))
	badge_apac_partner_july_2018_south_korea = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_apac_partner_july_2018_5_title", "Pokémon GO Special Weekend"), help_text=pgettext_lazy("badge_apac_partner_july_2018_5", "South Korea, July 29, 2018"))
	badge_yokosuka_29_aug_2018_mikasa = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_29_aug_2018_mikasa_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_29_aug_2018_mikasa", "Yokosuka, Aug 29, 2018-MIKASA"))
	badge_yokosuka_29_aug_2018_verny = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_29_aug_2018_verny_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_29_aug_2018_verny", "Yokosuka, Aug 29, 2018-VERNY"))
	badge_yokosuka_29_aug_2018_kurihama = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_29_aug_2018_kurihama_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_29_aug_2018_kurihama", "Yokosuka, Aug 29, 2018-KURIHAM"))
	badge_yokosuka_30_aug_2018_mikasa = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_30_aug_2018_mikasa_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_30_aug_2018_mikasa", "Yokosuka, Aug 30, 2018-MIKASA"))
	badge_yokosuka_30_aug_2018_verny = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_30_aug_2018_verny_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_30_aug_2018_verny", "Yokosuka, Aug 30, 2018-VERNY"))
	badge_yokosuka_30_aug_2018_kurihama = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_30_aug_2018_kurihama_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_30_aug_2018_kurihama", "Yokosuka, Aug 30, 2018-KURIHAMA"))
	badge_yokosuka_31_aug_2018_mikasa = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_31_aug_2018_mikasa_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_31_aug_2018_mikasa", "Yokosuka, Aug 31, 2018-MIKASA"))
	badge_yokosuka_31_aug_2018_verny = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_31_aug_2018_verny_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_31_aug_2018_verny", "Yokosuka, Aug 31, 2018-VERNY"))
	badge_yokosuka_31_aug_2018_kurihama = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_31_aug_2018_kurihama_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_31_aug_2018_kurihama", "Yokosuka, Aug 31, 2018-KURIHAMA"))
	badge_yokosuka_1_sep_2018_mikasa = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_1_sep_2018_mikasa_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_1_sep_2018_mikasa", "Yokosuka, Sep 1, 2018-MIKASA"))
	badge_yokosuka_1_sep_2018_verny = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_1_sep_2018_verny_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_1_sep_2018_verny", "Yokosuka, Sep 1, 2018-VERNY"))
	badge_yokosuka_1_sep_2018_kurihama = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_1_sep_2018_kurihama_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_1_sep_2018_kurihama", "Yokosuka, Sep 1, 2018-KURIHAMA"))
	badge_yokosuka_2_sep_2018_mikasa = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_2_sep_2018_mikasa_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_2_sep_2018_mikasa", "Yokosuka, Sep 2, 2018-MIKASA"))
	badge_yokosuka_2_sep_2018_verny = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_2_sep_2018_verny_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_2_sep_2018_verny", "Yokosuka, Sep 2, 2018-VERNY"))
	badge_yokosuka_2_sep_2018_kurihama = models.BooleanField(default=False, verbose_name=pgettext_lazy("badge_yokosuka_2_sep_2018_kurihama_title", "Pokémon GO Safari Zone"), help_text=pgettext_lazy("badge_yokosuka_2_sep_2018_kurihama", "Yokosuka, Sep 2, 2018-KURIHAMA"))
	
	leaderboard_country = models.ForeignKey(Country, on_delete=models.SET_NULL , null=True, blank=True, verbose_name=_("Country"), related_name='leaderboard_trainers_country', help_text=_("Where are you based?"))
	leaderboard_region = models.ForeignKey(Region, on_delete=models.SET_NULL , null=True, blank=True, verbose_name=_("Region"), related_name='leaderboard_trainers_region', help_text=_("Where are you based?"))
	
	verified = models.BooleanField(default=False, verbose_name=_("Verified"))
	last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last Modified"))
	
	event_10b = models.BooleanField(default=False)
	event_1k_users = models.BooleanField(default=False)
	
	verification = models.ImageField(upload_to=VerificationImagePath, blank=True, verbose_name=_("Username / Level / Team Screenshot"))
	
	thesilphroad_username = postgres_fields.CICharField(null=True, blank=True, max_length=30, verbose_name=_("TheSilphRoad Trainer Name"), help_text=_("The username you use on The Silph Road, if different from your Trainer Nickname.")) # max_length=15, unique=True, validators=[PokemonGoUsernameValidator]
	
	def has_cheated(self):
		return bool(self.last_cheated)
	has_cheated.boolean = True
	has_cheated.short_description = _("Historic Cheater")
	
	def currently_cheats(self):
		if self.last_cheated and self.last_cheated+timedelta(weeks=26) > timezone.now().date():
			return True
		else:
			return False
	currently_cheats.boolean = True
	currently_cheats.short_description = _("Cheater")
	
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
	awaiting_verification.short_description = _("Ready to be verified!")
	
	def is_verified(self):
		return self.verified
	is_verified.boolean = True
	is_verified.short_description = _("Verified")
	
	def is_verified_and_saved(self):
		return bool(bool(self.verified) and bool(self.verification))
	is_verified_and_saved.boolean = True
	
	def is_on_leaderboard(self):
		return bool(self.is_verified and self.statistics and not self.currently_cheats())
	is_on_leaderboard.boolean = True
	
	def level(self):
		update = self.update_set.exclude(xp__isnull=True)
		if update.exists():
			return level_parser(xp=update.aggregate(models.Max('xp'))['xp__max']).level
		return None
	
	def __str__(self):
		return self.username
	
	def circled_level(self):
		level = self.level()
		if level:
			return int_to_unicode(level).strip()
		return None
	
	def get_silph_card(self, make_assumption=True):
		if make_assumption:
			name = self.thesilphroad_username or self.username
		else:
			if self.thesilphroad_username:
				name = self.thesilphroad_username
			else:
				raise ObjectDoesNotExist
		r = requests.get('https://sil.ph/{}.json'.format(name))
		if r.status_code != 200:
			raise ObjectDoesNotExist
		try:
			r = r.json()
		except json.JSONDecodeError:
			raise ObjectDoesNotExist
		if 'data' in r:
			return r['data']
		else:
			raise PermissionDenied
	
	def get_silph_card_badges (self):
		badges = self.get_silph_card()['badges']
		try:
			return [x['Badge'] for x in self.get_silph_card()['badges'] if x['Badge']['slug'] not in ['travler-card']]
		except:
			return None
	
	def get_silph_card_id (self):
		return self.get_silph_card()['card_id']
	
	def get_silph_card_checkins (self):
		return self.get_silph_card()['checkins']
	
	def get_silph_card_goal (self):
		return self.get_silph_card()['goal']
	
	def get_silph_card_handshakes (self):
		return self.get_silph_card()['handshakes']
	
	def get_silph_card_home_region (self):
		return self.get_silph_card()['home_region']
	
	def get_silph_card_in_game_username (self):
		return self.get_silph_card()['in_game_username']
	
	def get_silph_card_joined (self):
		import pendulum
		return pendulum.parse(self.get_silph_card()['joined'])
	
	def get_silph_card_nest_migrations(self):
		return self.get_silph_card()['nest_migrations']
	
	def get_silph_card_playstyle(self):
		return self.get_silph_card()['playstyle']
	
	def get_silph_card_pokedex_count(self):
		return self.get_silph_card()['pokedex_count']
	
	def get_true_pokedex_count(self):
		try:
			silph_value = self.get_silph_card(make_assumption=False)['pokedex_count']
		except (ObjectDoesNotExist,PermissionDenied):
			silph_value = 0
		return max(silph_value, self.update_set.exclude(dex_caught__isnull=True).aggregate(Max('dex_caught')))
	
	def get_silph_card_team(self):
		return self.get_silph_card()['team']
	
	def get_silph_card_title(self):
		return self.get_silph_card()['title']
	
	def get_silph_card_xp(self):
		return self.get_silph_card()['xp']
	
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
		if self.thesilphroad_username:
			if self.faction.slug.casefold() != self.get_silph_card_team().casefold():
				raise ValidationError({'thesilphroad_username': _("The team of this Silph Card does not match that of your profile.")})
	
	def get_absolute_url(self):
		return reverse('trainerdex_web:profile_username', kwargs={'username':self.username})
	
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
	slug = models.SlugField()
	name_en = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('English')
		)
	)
	name_ja = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Japanese')
		)
	)
	name_fr = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('French')
		)
	)
	name_es = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Spanish')
		)
	)
	name_de = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('German')
		)
	)
	name_it = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Italian')
		)
	)
	name_ko = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Korean')
		)
	)
	name_zh_Hant = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Traditional Chinese')
		)
	)
	name_pt_BR = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Brazilian Portuguese')
		)
	)
	colour = RGBColorField(default='#929292', null=True, blank=True, verbose_name=_("Colour"))
	
	@property
	def image(self):
		return f'img/{self.slug}.png'
	
	@property
	def vector_image(self):
		return f'img/{self.slug}.svg'
	
	@property
	def localized_name(self):
		lng_cd = to_locale(get_supported_language_variant(get_language()))
		return getattr(self, f'name_{lng_cd}')
	
	def __str__(self):
		return f'{self.localized_name}'
	
	class Meta:
		verbose_name = _("Team")
		verbose_name_plural = _("Teams")
		
class FactionLeader(models.Model):
	faction = models.OneToOneField(Faction, on_delete=models.CASCADE, related_name='leader', verbose_name=_("Team"), primary_key=True)
	name_en = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('English')
		)
	)
	name_ja = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Japanese')
		)
	)
	name_fr = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('French')
		)
	)
	name_es = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Spanish')
		)
	)
	name_de = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('German')
		)
	)
	name_it = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Italian')
		)
	)
	name_ko = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Korean')
		)
	)
	name_zh_Hant = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Traditional Chinese')
		)
	)
	name_pt_BR = models.CharField(
		max_length=50,
		verbose_name=_("Name ({language})").format(
			language=_('Brazilian Portuguese')
		)
	)
	
	@property
	def localized_name(self):
		lng_cd = to_locale(get_supported_language_variant(get_language()))
		return getattr(self, f'name_{lng_cd}')
	
	def __str__(self):
		return f'{self.localized_name}, Leader of {self.faction}'
		
	class Meta:
		verbose_name = _("Team Leader")
		verbose_name_plural = _("Team Leaders")

class Update(models.Model):
	uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name="UUID")
	trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, verbose_name=_("Trainer"))
	update_time = models.DateTimeField(default=timezone.now, verbose_name=_("Time Updated"))
	xp = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("PROFILE_TOTAL_XP", "Total XP"), help_text=_("Your Total XP can be found at the bottom of your Pokémon Go profile"))
	dex_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("pokedex_page_caught", "Caught"), help_text=_("In your Pokédex, how many differnt species have you caught? It should say at the top."))
	dex_seen = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("pokedex_page_seen", "Seen"), help_text=_("In your Pokédex, how many differnt species have you seen? It should say at the top."))
	gym_badges = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("profile_category_gymbadges", "Gym Badges"), help_text=_("Your gym badges map. Total number of gold, silver, bronze and blank combined. (This information is currently not used)"))
	
	walk_dist = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, verbose_name=pgettext_lazy("badge_travel_km_title", "Jogger"), help_text=pgettext_lazy("badge_travel_km", "Walk {0:0,g} km").format(1000.0))
	gen_1_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_pokedex_entries_title", "Kanto"), help_text=pgettext_lazy("badge_pokedex_entries", "Register {0:0,} Kanto region Pokémon in the Pokédex.").format(100))
	pkmn_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_capture_total_title", "Collector"), help_text=pgettext_lazy("badge_capture_total", "Catch {0:0,} Pokémon.").format(2000))
	pkmn_evolved = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_evolved_total_title", "Scientist"), help_text=pgettext_lazy("badge_evolved_total", "Evolve {0:0,} Pokémon.").format(200))
	eggs_hatched = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_hatched_total_title", "Breeder"), help_text=pgettext_lazy("badge_hatched_total", "Hatch {0:0,} eggs.").format(500))
	pkstops_spun = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_pokestops_visited_title", "Backpacker"), help_text=pgettext_lazy("badge_pokestops_visited", "Visit {0:0,} PokéStops.").format(2000))
	battles_won = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_battle_attack_won_title", "Battle Girl"), help_text=pgettext_lazy("badge_battle_attack_won", "Win {0:0,} Gym battles.").format(1000))
	big_magikarp = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_big_magikarp_title", "Fisherman"), help_text=pgettext_lazy("badge_big_magikarp", "Catch {0:0,} big Magikarp.").format(300))
	legacy_gym_trained = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_battle_training_won_title", "Ace Trainer"), help_text=pgettext_lazy("badge_battle_training_won", "Train {0:0,} times.").format(1000))
	tiny_rattata = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_small_rattata_title", "Youngster"), help_text=pgettext_lazy("badge_small_rattata", "Catch {0:0,} tiny Rattata.").format(300))
	pikachu_caught = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_pikachu_title", "Pikachu Fan"), help_text=pgettext_lazy("badge_pikachu", "Catch {0:0,} Pikachu.").format(300))
	gen_2_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_pokedex_entries_gen2_title", "Johto"), help_text=pgettext_lazy("badge_pokedex_entries_gen2", "Register {0:0,} Pokémon first discovered in the Johto region to the Pokédex.").format(70))
	unown_alphabet = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_unown_title", "Unown"), help_text=pgettext_lazy("badge_unown", "Catch {0:0,} Unown.").format(26))
	berry_fed = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_berries_fed_title", "Berry Master"), help_text=pgettext_lazy("badge_berries_fed", "Feed {0:0,} Berries at Gyms.").format(1000))
	gym_defended = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_hours_defended_title", "Gym Leader"), help_text=pgettext_lazy("badge_hours_defended", "Defend Gyms for {0:0,} hours.").format(1000))
	raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_raid_battle_won_title", "Champion"), help_text=pgettext_lazy("badge_raid_battle_won", "Win {0:0,} Raids.").format(1000))
	leg_raids_completed = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_legendary_battle_won_title", "Battle Legend"), help_text=pgettext_lazy("badge_legendary_battle_won", "Win {0:0,} Legendary Raids.").format(1000))
	gen_3_dex = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_pokedex_entries_gen3_title", "Hoenn"), help_text=pgettext_lazy("badge_pokedex_entries_gen3", "Register {0:0,} Pokémon first discovered in the Hoenn region to the Pokédex.").format(90))
	quests = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_challenge_quests_title", "Pokémon Ranger"), help_text=pgettext_lazy("badge_challenge_quests", "Complete {0:0,} Field Research tasks.").format(1000))
	max_friends = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_max_level_friends_title", "Idol"), help_text=pgettext_lazy("badge_max_level_friends", "Become Best Friends with {0:0,} Trainers.").format(3))
	trading = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_trading_title", "Gentleman"), help_text=pgettext_lazy("badge_trading", "Trade {0:0,} Pokémon.").format(1000))
	trading_distance = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_trading_distance_title", "Pilot"), help_text=pgettext_lazy("badge_trading_distance", "Earn {0:0,} km across the distance of all Pokémon trades.").format(1000000))
	
	pkmn_normal = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_normal_title", "Schoolkid"), help_text=pgettext_lazy("badge_type_normal", "Catch {0:0,} Normal-type Pokémon").format(200))
	pkmn_fighting = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_fighting_title", "Black Belt"), help_text=pgettext_lazy("badge_type_fighting", "Catch {0:0,} Fighting-type Pokémon").format(200))
	pkmn_flying = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_flying_title", "Bird Keeper"), help_text=pgettext_lazy("badge_type_flying", "Catch {0:0,} Flying-type Pokémon").format(200))
	pkmn_poison = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_poison_title", "Punk Girl"), help_text=pgettext_lazy("badge_type_poison", "Catch {0:0,} Poison-type Pokémon").format(200))
	pkmn_ground = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_ground_title", "Ruin Maniac"), help_text=pgettext_lazy("badge_type_ground", "Catch {0:0,} Ground-type Pokémon").format(200))
	pkmn_rock = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_rock_title", "Hiker"), help_text=pgettext_lazy("badge_type_rock", "Catch {0:0,} Rock-type Pokémon").format(200))
	pkmn_bug = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_bug_title", "Bug Catcher"), help_text=pgettext_lazy("badge_type_bug", "Catch {0:0,} Bug-type Pokémon").format(200))
	pkmn_ghost = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_ghost_title", "Hex Maniac"), help_text=pgettext_lazy("badge_type_ghost", "Catch {0:0,} Ghost-type Pokémon").format(200))
	pkmn_steel = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_steel_title", "Depot Agent"), help_text=pgettext_lazy("badge_type_steel", "Catch {0:0,} Steel-type Pokémon").format(200))
	pkmn_fire = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_fire_title", "Kindler"), help_text=pgettext_lazy("badge_type_fire", "Catch {0:0,} Fire-type Pokémon").format(200))
	pkmn_water = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_water_title", "Swimmer"), help_text=pgettext_lazy("badge_type_water", "Catch {0:0,} Water-type Pokémon").format(200))
	pkmn_grass = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_grass_title", "Gardener"), help_text=pgettext_lazy("badge_type_grass", "Catch {0:0,} Grass-type Pokémon").format(200))
	pkmn_electric = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_electric_title", "Rocker"), help_text=pgettext_lazy("badge_type_electric", "Catch {0:0,} Electric-type Pokémon").format(200))
	pkmn_psychic = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_psychic_title", "Psychic"), help_text=pgettext_lazy("badge_type_psychic", "Catch {0:0,} Pychic-type Pokémon").format(200))
	pkmn_ice = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_ice_title", "Skier"), help_text=pgettext_lazy("badge_type_ice", "Catch {0:0,} Ice-type Pokémon").format(200))
	pkmn_dragon = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_dragon_title", "Dragon Tamer"), help_text=pgettext_lazy("badge_type_dragon", "Catch {0:0,} Dragon-type Pokémon").format(200))
	pkmn_dark = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_dark_title", "Delinquent"), help_text=pgettext_lazy("badge_type_dark", "Catch {0:0,} Dark-type Pokémon").format(200))
	pkmn_fairy = models.PositiveIntegerField(null=True, blank=True, verbose_name=pgettext_lazy("badge_type_fairy_title", "Fairy Tale Girl"), help_text=pgettext_lazy("badge_type_fairy", "Catch {0:0,} Fairy-type Pokémon").format(200))
	
	stardust = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Stardust"))
	
	meta_time_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Time Created"))
	DATABASE_SOURCES = (
		('?', None),
		('cs_social_twitter', 'Twitter (Found)'),
		('cs_social_facebook', 'Facebook (Found)'),
		('cs_social_youtube', 'YouTube (Found)'),
		('cs_?', 'Sourced Elsewhere'),
		('ts_social_discord', 'Discord'),
		('ts_social_twitter', 'Twitter'),
		('ts_direct', 'Directly told (via text)'),
		('web_quick', 'Quick Update (Web)'),
		('web_detailed', 'Detailed Update (Web)'),
		('ts_registration', 'Registration'),
		('ss_registration', 'Registration w/ Screenshot'),
		('ss_generic', 'Generic Screenshot'),
		('ss_ocr', "OCR Screenshot"),
		('com.nianticlabs.pokemongo.friends', "In Game Friends"),
		('com.pokeassistant.trainerstats', "Poké Assistant"),
		('com.pokenavbot.profiles', "PokeNav"),
		('tl40datateam.spreadsheet', "Tl40 Data Team"),
		('com.pkmngots.import', "Third Saturday"),
	)
	meta_source = models.CharField(max_length=256, choices=DATABASE_SOURCES, default='?', verbose_name=_("Source"))
	
	image_proof = models.ImageField(upload_to=VerificationUpdateImagePath, blank=True, verbose_name=_("Total XP Screenshot"))
	
	def meta_crowd_sourced(self):
		if self.meta_source.startswith('cs'):
			return True
		elif self.meta_source == ('?'):
			return None
		return False
	meta_crowd_sourced.boolean = True
	meta_crowd_sourced.short_description = _("Crowd Sourced")
	
	def modified_extra_fields(self):
		return bool([x for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('dex_caught', 'dex_seen', 'gym_badges')) if getattr(self, x)])
	modified_extra_fields.boolean = True
	
	def __str__(self):
		if self.xp:
			if self.modified_extra_fields():
				return _("{username} - {xp:,}XP and {stats_num} stats updated at {date}").format(username=self.trainer.username, xp=self.xp, stats_num=sum([bool(getattr(self, x)) for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('dex_caught', 'dex_seen', 'gym_badges'))]), date=self.update_time.isoformat(sep=' ', timespec='minutes'))
			else:
				return _("{username} - {xp:,}XP at {date}").format(username=self.trainer.username, xp=self.xp, date=self.update_time.isoformat(sep=' ', timespec='minutes'))
		else:
			return _("{username} - {stats_num} stats updated at {date}").format(username=self.trainer.username, stats_num=sum([bool(getattr(self, x)) for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('xp', 'dex_caught', 'dex_seen', 'gym_badges'))]), date=self.update_time.isoformat(sep=' ', timespec='minutes'))
	
	def clean(self):
		
		error_dict = {}
		try: # Workaround for inital registrations
			if bool(self.trainer.start_date) and (self.update_time.date() < self.trainer.start_date):
				error_dict['update_time'] = ValidationError(_("You can't post before your start date."))

			for field in Update._meta.get_fields():
				if field.name in UPDATE_NON_REVERSEABLE_FIELDS and bool(getattr(self, field.name)):
					# Get latest update with that field present, only get the important fields.
					largest = self.trainer.update_set.filter(update_time__lt=self.update_time).exclude(**{field.name : None}).order_by('-'+field.name).only(field.name, 'update_time').first()
					if bool(largest) and bool(getattr(self, field.name)):
						if getattr(self, field.name) < getattr(largest, field.name):
							error_dict[field.name] = ValidationError(_("This value has previously been entered at a higher value. Please try again ensuring the value you entered was correct."))
						elif getattr(self, field.name) == getattr(largest, field.name):
							if field.name in ['gen_1_dex','gen_2_dex','gen_3_dex','unown_alphabet'] and getattr(self, field.name) >= {'gen_1_dex':151,'gen_2_dex':100,'gen_3_dex':135,'unown_alphabet':28}[field.name]:
								# Field is max'd, empty value
								setattr(self, field.name, None)
							else:
								# Field isn't maxable, let it be stored
								pass
						
					# Field specific Validation
					
					# 1 - Ace Trainer
					if field.name == 'legacy_gym_trained' and self.update_time.date() > date(2017,6,19):
						if bool(largest) and largest.update_time.date() == date(2017,6,19):
							pass
						else:
							if bool(self.trainer.start_date) and self.trainer.start_date <= date(2017,6,19):
								maybe_create = Update(trainer=self.trainer, update_time=datetime(2017,6,19,20,00), legacy_gym_trained=self.legacy_gym_trained)
							else:
								maybe_create = None
							self.legacy_gym_trained = None
							
					# 2 - berry_fed, gyms_defended, raids_completed
					if field.name in ['berry_fed', 'gym_defended', 'raids_completed'] and self.update_time.date() < date(2016,6,22):
						setattr(self, field.name, None)
					
					# 3 - leg_raids_completed
					# More validation needed - rest of world got it later
					if field.name == 'leg_raids_completed' and self.update_time.date() < date(2017,7,22):
						setattr(self, field.name, None)
					
					# 4 - gen_1_dex
					GEN_1_MAX = 151
					if field.name == 'gen_1_dex' and bool(getattr(self, field.name)) and getattr(self, field.name) > GEN_1_MAX:
						error_dict[field.name] = ValidationError(_(f"There are only {GEN_1_MAX} Pokémon in the Kanto region."))
					
					# 5 gen_2_dex
					# More validation needed - how many and when?
					GEN_2_MAX = 100
					if field.name == 'gen_2_dex' and bool(getattr(self, field.name)) and getattr(self, field.name) > GEN_2_MAX:
						error_dict[field.name] = ValidationError(_(f"There are only {GEN_2_MAX} Pokémon in the Johto region."))
					if field.name == 'gen_2_dex' and bool(getattr(self, field.name)) and self.update_time.date() < date(2017,2,10):
						setattr(self, field.name, None)
					
					# 6 - gen_3_dex
					# More validation needed - how many and when?
					GEN_3_MAX = 135
					if field.name == 'gen_3_dex' and bool(getattr(self, field.name)) and getattr(self, field.name) > GEN_3_MAX:
						error_dict[field.name] = ValidationError(_(f"There are only {GEN_3_MAX} Pokémon in the Hoenn region."))
					if field.name == 'gen_3_dex' and bool(getattr(self, field.name)) and self.update_time.date() < date(2017,10,20):
						setattr(self, field.name, None)
					
					# 7 - quests
					if field.name == 'quests' and self.update_time.date() < date(2018,3,30):
						setattr(self, field.name, None)
				
					# 8 - quests
					if field.name in ['max_friends','trading','trading_distance'] and self.update_time.date() < date(2018,6,21):
						setattr(self, field.name, None)
					
					# 9 - unown_alphabet
					UNOWN_MAX = 28
					if field.name == 'unown_alphabet' and bool(getattr(self, field.name)) and getattr(self, field.name) > UNOWN_MAX:
						error_dict[field.name] = ValidationError(_(f"There are only {UNOWN_MAX} different forms of Unown."))
					
						
		except Exception as e:
			if str(e) != 'Update has no trainer.':
				raise e
		
		if (Update.objects.filter(trainer=self.trainer, xp__isnull=False).count() == 0 and self.xp is None) or (Update.objects.filter(trainer=self.trainer, xp__isnull=False).count() == 1 and self.xp is None and self.uuid == Update.objects.filter(trainer=self.trainer, xp__isnull=False)[0].uuid):
			error_dict['xp'] = ValidationError('You need to enter an XP on your first update')
		
		if not any([getattr(self, x) for x in (UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES + ('xp', 'dex_caught', 'dex_seen', 'gym_badges'))]):
			raise ValidationError(_("No valid fields filled. If you only entered a field that is already max'd, this is why. We clear max'd fields."))

		if error_dict != {}:
			raise ValidationError(error_dict)
		elif maybe_create:
			maybe_create.save()
	
	class Meta:
		get_latest_by = 'update_time'
		ordering = ['-update_time']
		verbose_name = _("Update")
		verbose_name_plural = _("Updates")

#@receiver(post_save, sender=Update)
#def update_discord_level(sender, **kwargs):
#	if kwargs['created'] and kwargs['instance'].xp:
#		if kwargs['instance'].trainer.owner.socialaccount_set.filter(provider='discord').exists():
#			for user in kwargs['instance'].trainer.owner.socialaccount_set.filter(provider='discord'):
#				r = requests.get(
#					url="https://discordapp.com/api/v6/users/@me/guilds",
#					headers={"Authorization": "Bearer {oauth2_token}".format(
#						oauth2_token=user.socialtoken_set.first().token
#					)})
#				if 'code' in r.json():
#					return
#				for guild in DiscordGuild.objects.filter(id__in=[x['id'] for x in r.json()], setting_rename_users=True):
#					check = requests.get(
#						url="https://discordapp.com/api/v6/guilds/{guild}/members/{user}".format(
#							guild = guild.id,
#							user = user.uid
#						),
#						headers = {"Authorization": "Bot {token}".format(
#							token="Mzc3NTU5OTAyNTEzNzkwOTc3.Da5Omg.SQf0EuGcHS3Sp0GCRluKaM6Crrw")}
#					)
#
#					try:
#						if check.json()['nick']:
#							base_name = check.json()['nick']
#						else:
#							base_name = kwargs['instance'].trainer.username
#					except KeyError:
#						base_name = kwargs['instance'].trainer.username
#
#					if ord(base_name[-1]) in numbers:
#						base_name = base_name[:-2]
#
#					new_name = base_name+" "+int_to_unicode(kwargs['instance'].trainer.level())
#
#					logger.info("Renaming {user} on Discord Guild #{guild_id} to {name}".format(
#						user=kwargs['instance'].trainer.username,
#						guild_id=guild.id,
#						name=new_name
#					))
#
#					edit = requests.patch(
#						url="https://discordapp.com/api/v6/guilds/{guild}/members/{user}".format(
#							guild = guild.id,
#							user = user.uid
#						),
#						headers={"Authorization": "Bot {token}".format(
#							token="Mzc3NTU5OTAyNTEzNzkwOTc3.Da5Omg.SQf0EuGcHS3Sp0GCRluKaM6Crrw")},
#						json={"nick": new_name})
#
#					if edit.status_code != 204:
#						logger.error("^ {code} ^ Failed to rename user, trying again \n {log}".format(
#							code=edit.status_code,
#							log=edit.content))
#
#						# I'm not 100% sure tryiing again will ever work. Maybe a workaround could be messaging the user via one of the set OCR channels and letting them know the bot in unable to rename them and they'll have to manage it themselves.
#
#						edit = requests.patch(
#							url="https://discordapp.com/api/v6/guilds/{guild}/members/{user}".format(
#								guild = guild.id,
#								user = user.uid
#							),
#							headers={"Authorization": "Bearer {oauth2_token}".format(oauth2_token=user.socialtoken_set.first().token)},
#							json={"nick": new_name})
#
#						if edit.status_code != 204:
#							logger.error("^ {code} ^ Failed to rename user again \n {log}".format(
#								code=edit.status_code,
#								log=edit.content))

class TrainerReport(models.Model):
	trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name=_("Trainer"))
	reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Reported by"))
	report = models.TextField(verbose_name=_("Report"))
	
	class Meta:
		verbose_name=_("Report")
		verbose_name_plural=_("Reports")

class Sponsorship(models.Model):
	slug = models.SlugField(db_index=True, primary_key=True)
	title = models.CharField(db_index=True, max_length=20)
	description = models.CharField(db_index=True, max_length=240)
	icon = models.ImageField(upload_to='spon/')
	members = models.ManyToManyField(Trainer, related_name='sponsorships')
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = _("Special Relationship (Sponsorship)")
		verbose_name_plural = _("Special Relationships (Sponsorships)")

class DiscordGuild(models.Model):
	id = models.BigIntegerField(primary_key=True)
	cached_data = postgres_fields.JSONField(null=True, blank=True)
	cached_date = models.DateTimeField(auto_now=True)
	
	setting_channels_ocr_enabled = postgres_fields.ArrayField(models.BigIntegerField())
	setting_rename_users = models.BooleanField(default=False)
	
	def __str__(self):
		return str(self.id)
	
	class Meta:
		verbose_name = _("Discord Guild")
		verbose_name_plural = _("Discord Guilds")

class CommunityLeague(models.Model):
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
		through='CommunityLeagueMembershipPersonal',
		through_fields=('league', 'trainer')
	)
	memberships_discord = models.ManyToManyField(
		DiscordGuild,
		through='CommunityLeagueMembershipDiscord',
		through_fields=('league', 'discord')
	)
	
	def __str__(self):
		return self.short_description
	
	class Meta:
		verbose_name = _("Community League")
		verbose_name_plural = _("Community Leagues")

class CommunityLeagueMembershipPersonal(models.Model):
	league = models.ForeignKey(CommunityLeague, on_delete=models.CASCADE)
	trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
	
	primary = models.BooleanField(default=True)
	
	def __str__(self):
		return "{league} - {trainer}".format(league=self.league, trainer=self.trainer)
	
	class Meta:
		verbose_name = _("Community League Membership")
		verbose_name_plural = _("Community League Memberships")

class CommunityLeagueMembershipDiscord(models.Model):
	league = models.ForeignKey(CommunityLeague, on_delete=models.CASCADE)
	discord = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)
	
	auto_import = models.BooleanField(default=True)
	
	security_ban_sync = models.NullBooleanField()
	security_kick_sync = models.NullBooleanField()
	
	def __str__(self):
		return "{league} - {guild}".format(league=self.league, trainer=self.discord)
	
	class Meta:
		verbose_name = _("Community League Discord Connection")
		verbose_name_plural = _("Community League Discord Connections")
