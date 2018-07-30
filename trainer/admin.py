# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from trainer.models import *

admin.site.register(Faction)
admin.site.register(DiscordGuild)
admin.site.register(PrivateLeague)
admin.site.register(PrivateLeagueMembershipPersonal)
admin.site.register(PrivateLeagueMembershipDiscord)

@admin.register(TrainerReport)
class TrainerReportAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(TrainerReport, {
		'trainer' : 'trainer'
	})

@admin.register(Sponsorship)
class SponsorshipAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Sponsorship, {
		'members' : 'trainer'
	})

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
			'fields': ('owner', 'username', 'faction', 'start_date', 'daily_goal', 'total_goal','trainer_code', 'thesilphroad_username')
		}),
		(_('Reports'), {
			'fields': ('has_cheated', 'last_cheated', 'currently_cheats', 'verified', 'verification')
		}),
		(_('2017 Events'), {
			'classes': ('collapse',),
			'fields': ('badge_chicago_fest_july_2017', 'badge_pikachu_outbreak_yokohama_2017', 'badge_safari_zone_europe_2017_09_16', 'badge_safari_zone_europe_2017_10_07', 'badge_safari_zone_europe_2017_10_14')
		}),
		(_('2018 Events'), {
			'classes': ('collapse',),
			'fields': ('badge_chicago_fest_july_2018','badge_apac_partner_july_2018')
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
	
