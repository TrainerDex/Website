from django.contrib import admin
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from website.models import *

@admin.register(Discord)
class DiscordAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Discord, {
		'locations' : 'cities_light_city'
	})
	list_display = ('name', 'locations', 'invite_slug')
	search_fields = ('name','locations')

@admin.register(WhatsApp)
class WhatsAppAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(WhatsApp, {
		'locations' : 'cities_light_city'
	})
	list_display = ('name', 'locations', 'invite_slug')
	search_fields = ('name','locations')

@admin.register(FacebookGroup)
class FacebookGroupAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(FacebookGroup, {
		'locations' : 'cities_light_city'
	})
	list_display = ('name', 'locations', 'username')
	search_fields = ('name','locations')

@admin.register(MessengerGroup)
class MessengerGroupAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(MessengerGroup, {
		'locations' : 'cities_light_city'
	})
	list_display = ('name', 'locations', 'invite_slug')
	search_fields = ('name','locations')
