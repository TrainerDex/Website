# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add
from trainer.models import *

admin.site.register(Faction)

class XUserInline(admin.StackedInline):
	model = ExtendedProfile
	can_delete = False

class UserAdmin(BaseUserAdmin):
	inlines = (XUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Update)
class UpdateAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Update, {
		'trainer': 'trainer'
	})
	list_display = ('trainer', 'xp', 'datetime')
	search_fields = ('trainer__username', 'trainer__account__username')
	ordering = ('-datetime',)
	
@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'account': 'user'
	})
	list_display = ('username', 'faction', 'currently_cheats', 'statistics')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics', 'prefered')
	search_fields = ('username', 'account__username', 'account__first_name', 'faction__name')
	ordering = ('username',)

@admin.register(DiscordUser)
class DiscordUserAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(DiscordUser, {
		'account': 'user'
	})

@admin.register(DiscordServer)
class DiscordServerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(DiscordServer, {
		'owner': 'user'
	})
