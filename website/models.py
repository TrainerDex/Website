# -*- coding: utf-8 -*-
import os
from cities.models import Country, Region, Subregion, City, District
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import *
from django.utils.translation import ugettext_lazy as _
from trainer.models import Faction

DEFAULT_TEAM_ID=0

class BaseCommunity(models.Model):
	id = models.CharField(max_length=256, primary_key=True)
	name = models.CharField(max_length=140, verbose_name = _("Name"))
	countries = models.ManyToManyField(Country, blank=True)
	regions = models.ManyToManyField(Region, blank=True)
	subregions = models.ManyToManyField(Subregion, blank=True)
	cities = models.ManyToManyField(City, blank=True)
	districts = models.ManyToManyField(District, blank=True)
	team = models.ForeignKey(Faction, default=DEFAULT_TEAM_ID, verbose_name = _("Team"))
	description = models.CharField(max_length=140, blank=True, verbose_name = _("Description"))
	long_description = models.TextField(blank=True, verbose_name = _("Long Description"))
	extra_data = models.TextField(blank=True)
	invite_override_url = models.URLField(null=True, blank=True)
	invite_override_note = models.CharField(max_length=100, null=True, blank=True)
	
	def is_invite_override(self):
		return True if self.invite_override_url is not None or self.invite_override_note is not None else False
	is_invite_override.boolean = True
	
	@property
	def locations(self):
		return list(self.countries.all())+list(self.regions.all())+list(self.subregions.all())+list(self.cities.all())+list(self.districts.all())
	
	def __str__(self):
		return self.name
	
	class Meta:
		abstract = True
		ordering = ['name']

class Discord(BaseCommunity):
	invite_slug = models.SlugField(unique=True)
	enhanced = models.BooleanField(default=False, verbose_name = _("Enhanced"))
	
	@property
	def invite(self):
		return "https://discord.gg/"+self.invite_slug
	
	def active(self):
		import requests
		r = requests.get('https://discordapp.com/api/invites/'+self.invite_slug)
		if r.json()['code'] == 10006:
			return False
		else:
			return True
	active.boolean = True
	
	@property
	def state(self):
		return 'live' if self.active is True else 'dead'
	
	@property
	def social(self):
		return 'discord-enhanced' if self.enhanced is True else 'discord'
	
	class Meta:
		verbose_name = _("Discord Server")
		verbose_name_plural = _("Discord Servers")

class WhatsApp(BaseCommunity):
	invite_slug = models.SlugField(max_length=100, unique=True)
	
	@property
	def invite(self):
		return "https://chat.whatsapp.com/invite/"+self.invite_slug if self.is_invite_override() is False else self.invite_override_url
	
	@property
	def state(self):
		return 'unknown'
	
	@property
	def social(self):
		return 'whatsapp'
	
	class Meta:
		verbose_name = _("WhatsApp Group")
		verbose_name_plural = _("WhatsApp Groups")

class FacebookGroup(BaseCommunity):
	username = models.SlugField(unique=True, null=True, blank=True)
	
	@property
	def invite_slug(self):
		return self.username if self.username is not None else self.id
	
	@property
	def invite(self):
		return "https://www.facebook.com/groups/"+self.invite_slug if self.is_invite_override() is False else self.invite_override_url
	
	@property
	def state(self):
		return 'unknown'
	
	@property
	def social(self):
		return 'facebook'
	
	class Meta:
		verbose_name = _("Facebook Group")
		verbose_name_plural = _("Facebook Groups")

class MessengerGroup(BaseCommunity):
	invite_slug = models.SlugField(max_length=100, unique=True)
	
	@property
	def invite(self):
		return "https://m.me/join/"+self.invite_slug if self.is_invite_override() is False else self.invite_override_url
	
	@property
	def state(self):
		return 'unknown'
	
	@property
	def social(self):
		return 'messenger'
	
	class Meta:
		verbose_name = _("Facebook Messenger Group")
		verbose_name_plural = _("Facebook Messenger Groups")
