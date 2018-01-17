# -*- coding: utf-8 -*-
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from website.models import *

@admin.register(Discord)
class DiscordAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Discord, {
		'countries' : 'countries',
		'regions': 'regions',
		'subregions' : 'subregions',
		'cities' : 'cities',
		'districts' : 'districts',
	})
	list_display = ('name', 'locations', 'team', 'invite_slug', 'is_invite_override', 'active')
	search_fields = ('name', 'locations')

@admin.register(WhatsApp)
class WhatsAppAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(WhatsApp, {
		'countries' : 'countries',
		'regions': 'regions',
		'subregions' : 'subregions',
		'cities' : 'cities',
		'districts' : 'districts',
	})
	list_display = ('name', 'locations', 'team', 'invite_slug', 'is_invite_override')
	search_fields = ('name', 'locations')

@admin.register(FacebookGroup)
class FacebookGroupAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(FacebookGroup, {
		'countries' : 'countries',
		'regions': 'regions',
		'subregions' : 'subregions',
		'cities' : 'cities',
		'districts' : 'districts',
	})
	list_display = ('name', 'locations', 'team', 'username', 'is_invite_override')
	search_fields = ('name', 'locations')

@admin.register(MessengerGroup)
class MessengerGroupAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(MessengerGroup, {
		'countries' : 'countries',
		'regions': 'regions',
		'subregions' : 'subregions',
		'cities' : 'cities',
		'districts' : 'districts',
	})
	list_display = ('name', 'locations', 'team', 'invite_slug', 'is_invite_override')
	search_fields = ('name', 'locations')
