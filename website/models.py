# -*- coding: utf-8 -*-
import os
from cities.models import Country, City
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
	location_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.SET_NULL)
	location_id = models.PositiveIntegerField(blank=True, null=True)
	location = GenericForeignKey('location_type', 'location_id')
	team = models.ForeignKey(Faction, default=DEFAULT_TEAM_ID)
	description = models.CharField(max_length=140, blank=True)
	long_description = models.TextField(blank=True)
	extra_data = models.TextField(blank=True)
	
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
	def social(self):
		return 'discord-enhanced' if self.enhanced is True else 'discord'

class WhatsApp(BaseCommunity):
	invite_slug = models.SlugField(max_length=100, unique=True)
	
	@property
	def invite(self):
		return "https://chat.whatsapp.com/invite/"+self.invite_slug
	
	@property
	def social(self):
		return 'whatsapp'

class FacebookGroup(BaseCommunity):
	username = models.SlugField(unique=True)
	
	@property
	def invite(self):
		return "https://www.facebook.com/groups/"+self.username
	
	@property
	def social(self):
		return 'facebook'

class MessengerGroup(BaseCommunity):
	invite_slug = models.SlugField(max_length=100, unique=True)
	
	@property
	def invite(self):
		return "https://m.me/join/"+self.invite_slug
	
	@property
	def social(self):
		return 'messenger'
