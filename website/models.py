# -*- coding: utf-8 -*-
import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *
from cities_light.models import City

class BaseCommunity(models.Model):
	id = models.CharField(max_length=256, primary_key=True)
	name = models.CharField(max_length=256)
	locations = models.ForeignKey(City, null=True, blank=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		abstract = True
		ordering = ['name']

class Discord(BaseCommunity):
	invite_slug = models.CharField(max_length=256)
	extra_data = models.TextField(blank=True)
	
	@property
	def invite(self):
		return "https://discord.gg/"+self.invite_slug
	
	@property
	def social(self):
		return 'discord'

class WhatsApp(BaseCommunity):
	invite_slug = models.CharField(max_length=256)
	extra_data = models.TextField(blank=True)
	
	@property
	def invite(self):
		return "https://chat.whatsapp.com/invite/"+self.invite_slug
	
	@property
	def social(self):
		return 'whatsapp'

class FacebookGroup(BaseCommunity):
	username = models.CharField(max_length=256)
	extra_data = models.TextField(blank=True)
	
	@property
	def invite(self):
		return "https://www.facebook.com/groups/"+self.username
	
	@property
	def social(self):
		return 'facebook'
