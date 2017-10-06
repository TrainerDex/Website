# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add
from trainer.models import *

admin.site.register(Faction)
admin.site.register(Report)

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
	
@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'account': 'user'
	})
	
@admin.register(Network)
class NetworkAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Network, {
		'owner': 'user',
		'discord_servers': 'discord_server'
	})
	
@admin.register(NetworkMember)
class NetworkMemberAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(NetworkMember, {
		'user': 'user',
		'network': 'network'
	})
	
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
	
@admin.register(DiscordMember)
class DiscordMemberAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(DiscordMember, {
		'user': 'user',
		'server': 'discord_server'
	})
	
@admin.register(Ban)
class BanAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Ban, {
		'user': 'user',
		'discord': 'discord_server',
		'network': 'network'
	})