# -*- coding: utf-8 -*-
import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *
from cities_light.models import City

class BaseCommunity(models.Model):
	name = models.CharField(max_length=256)
	locations = models.ManyToManyField(City)
	uri = models.URLField()
	
	def __str__(self):
		return self.name

class Discord(BaseCommunity):
	identifier = models.BigIntegerField()
	extra_data = models.TextField(blank=True)
