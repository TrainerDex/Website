# -*- coding: utf-8 -*-
import os
from cities.models import Country, Region, Subregion, City, District
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import *
from trainer.models import Faction

DEFAULT_TEAM_ID=0

class BaseCommunity(models.Model):
	id = models.CharField(max_length=256, primary_key=True)
	name = models.CharField(max_length=140)
	countries = models.ManyToManyField(Country, blank=True)
	regions = models.ManyToManyField(Region, blank=True)
	subregions = models.ManyToManyField(Subregion, blank=True)
	cities = models.ManyToManyField(City, blank=True)
	districts = models.ManyToManyField(District, blank=True)
	team = models.ForeignKey(Faction, default=DEFAULT_TEAM_ID)
	description = models.CharField(max_length=140, blank=True)
	long_description = models.TextField(blank=True)
	extra_data = models.TextField(blank=True)
	invite_override_url = models.URLField(null=True, blank=True)
	invite_override_note = models.CharField(max_length=100, null=True, blank=True)
	
	def is_invite_override(self):
		return True if self.invite_override_url is not None or self.invite_override_note is not None else False
	
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
	enhanced = models.BooleanField(default=False)
	
	@property
	def invite(self):
		return "https://discord.gg/"+self.invite_slug
	
	@property
	def active(self):
		import requests
		r = requests.get('https://discordapp.com/api/invites/'+self.invite_slug)
		if r.json()['code'] == 10006:
			return False
		else:
			return True
	
	@property
	def state(self):
		return 'live' if self.active is True else 'dead'
	
	@property
	def social(self):
		return 'discord-enhanced' if self.enhanced is True else 'discord'

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
