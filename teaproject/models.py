# -*- coding: utf-8 -*-
import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *
from colorful.fields import RGBColorField

class Tea(models.Model):
	name = models.CharField(max_length=75, unique=True)
	green = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']

class Sweetener(models.Model):
	name = models.CharField(max_length=75, unique=True)
	cube = models.BooleanField(default=False)
	packet = models.BooleanField(default=False)
	
	def __str__(self):
		stringg += self.name
		if self.cube is True:
			stringg += "Cube"
		elif self.packet is True:
			stringg += "Packet"
		return stringg
	
	class Meta:
		ordering = ['name']

class Colour(models.Model):
	name = models.CharField(max_length=75)
	colour = RGBColorField(primary_key=True)
	
	def __str__(self):
		return self.name

class Cuppa(models.Model):
	drinker = models.ForeignKey(User, on_delete=models.CASCADE)
	tea = model.ForeignKey(Tea, on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	sweetener_amt = models.PositiveIntegerField()
	sweetener_type = models.ForeignKey(Sweetener, on_delete=models.SET_NULL, null=True, blank=True)
	colour = models.ForeignKey(Colour, on_delete=models.SET_NULL, null=True, blank=True)
	iswaterhard = models.BooleanField(default=True)
	isbought = models.BooleanField(default=False)
	
	def __str__(self):
		return self.tea.name+'+str(self.datetime)
	
	class Meta:
		get_latest_by = 'datetime'
		ordering = ['-datetime']
