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
	list_display = ('trainer', 'xp', 'update_time', 'meta_crowd_sourced','meta_source')
	search_fields = ('trainer__username', 'trainer__owner__username')
	ordering = ('-update_time',)
	date_hierarchy = 'update_time'

@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'owner' : 'user',
		'leaderboard_country' : 'countries',
		'leaderboard_region': 'regions',
		'leaderboard_subregion' : 'subregions',
		'leaderboard_city' : 'cities',
	})
	list_display = ('username', 'faction', 'currently_cheats', 'statistics', 'verified')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics', 'verified')
	search_fields = ('username', 'owner__username', 'owner__first_name')
	ordering = ('username',)
	date_hierarchy = 'start_date'
	fieldsets = (
		(None, {
			'fields': ('owner', 'username', 'faction', 'start_date', 'statistics', 'daily_goal', 'total_goal', 'prefered')
		}),
		(_('Reports'), {
			'fields': ('has_cheated', 'last_cheated', 'currently_cheats', 'verified', 'active')
		}),
		(_('Events'), {
			'fields': ('go_fest_2017', 'outbreak_2017', 'safari_zone_2017_oberhausen', 'safari_zone_2017_paris', 'safari_zone_2017_barcelona', 'safari_zone_2017_copenhagen', 'safari_zone_2017_prague', 'safari_zone_2017_stockholm', 'safari_zone_2017_amstelveen')
		}),
		(_('Website Events'), {
			'fields': ('event_10b','event_1k_users')
		}),
		(_('Leaderboard'), {
			'fields': ('leaderboard_country', 'leaderboard_region', 'leaderboard_subregion', 'leaderboard_city')
		}),
	)
	
	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('event_10b','event_1k_users')
		return self.readonly_fields
	
