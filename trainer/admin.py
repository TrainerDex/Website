# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from trainer.models import *

admin.site.register(Faction)
admin.site.register(TrainerReport)

@admin.register(Update)
class UpdateAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Update, {
		'trainer' : 'trainer'
	})
	list_display = ('trainer', 'xp', 'update_time', 'meta_crowd_sourced','meta_source', 'modified_extra_fields')
	search_fields = ('trainer__username', 'trainer__owner__username')
	ordering = ('-update_time',)
	date_hierarchy = 'update_time'

@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'owner' : 'user',
		'leaderboard_country' : 'countries',
		'leaderboard_region': 'regions',
	})
	list_display = ('username', 'level', 'faction', 'currently_cheats', 'is_on_leaderboard', 'is_verified', 'awaiting_verification')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics', 'verified',)
	search_fields = ('username', 'owner__first_name')
	ordering = ('username',)
	fieldsets = (
		(None, {
			'fields': ('owner', 'username', 'faction', 'start_date', 'daily_goal', 'total_goal','trainer_code')
		}),
		(_('Reports'), {
			'fields': ('has_cheated', 'last_cheated', 'currently_cheats', 'verified', 'verification')
		}),
		(_('2017 Events'), {
			'classes': ('collapse',),
			'fields': ('go_fest_2017', 'outbreak_2017', 'safari_zone_2017_oberhausen', 'safari_zone_2017_paris', 'safari_zone_2017_barcelona', 'safari_zone_2017_copenhagen', 'safari_zone_2017_prague', 'safari_zone_2017_stockholm', 'safari_zone_2017_amstelveen')
		}),
		(_('2018 Events'), {
			'classes': ('collapse',),
			'fields': ('go_fest_2018',)
		}),
		(_('Website Badges'), {
			'fields': ('event_10b','event_1k_users')
		}),
		(_('Leaderboard'), {
			'fields': ('leaderboard_country', 'leaderboard_region', 'statistics')
		}),
	)
	
	def get_readonly_fields(self, request, obj=None): 
		if obj: # editing an existing object 
			return self.readonly_fields + ('event_10b','event_1k_users') 
		return self.readonly_fields
	
	def get_queryset(self, request):
		return super(TrainerAdmin,self).get_queryset(request).prefetch_related('update_set')
	
