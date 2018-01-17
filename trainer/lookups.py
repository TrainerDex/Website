# -*- coding: utf-8 -*-
from ajax_select import register, LookupChannel
from trainer.models import Trainer
from django.contrib.auth.models import User

@register('trainer')
class TrainerLookup(LookupChannel):
	
	model = Trainer
	
	def get_query(self, q, request):
		return self.model.objects.filter(username__icontains=q)
	
	def format_item_display(self, item):
		return u"<span class='tag'>%s</span>" % item.username

@register('user')
class UserLookup(LookupChannel):
	
	model = User
	
	def get_query(self, q, request):
		return self.model.objects.filter(username__icontains=q)
	
	def format_item_display(self, item):
		return u"<span class='tag'>%s</span>" % item.username
