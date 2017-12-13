from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from website.models import *

@admin.register(Discord)
class DiscordAdmin(AjaxSelectAdmin):
	
	list_display = ('name', 'invite_slug')
	search_fields = ('name',)

@admin.register(WhatsApp)
class WhatsAppAdmin(AjaxSelectAdmin):
	
	list_display = ('name', 'invite_slug')
	search_fields = ('name',)

@admin.register(FacebookGroup)
class FacebookGroupAdmin(AjaxSelectAdmin):
	
	list_display = ('name', 'username')
	search_fields = ('name',)

@admin.register(MessengerGroup)
class MessengerGroupAdmin(AjaxSelectAdmin):
	
	list_display = ('name', 'invite_slug')
	search_fields = ('name',)
