from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from trainer.models import *

class XUserInline(admin.StackedInline):
	model = ExtendedProfile
	can_delete = False

class UserAdmin(BaseUserAdmin):
	inlines = (XUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
	icon = '<i class="material-icons">warning</i>'

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
	
	raw_id_fields = ("trainer",)
	list_display = ('trainer', 'xp', 'datetime')
	search_fields = ('trainer__username', 'trainer__owner__username')
	ordering = ('-datetime',)
	date_hierarchy = 'datetime'
	icon = '<i class="material-icons">insert_chart</i>'

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
	
	raw_id_fields = ("owner",)
	list_display = ('username', 'faction', 'currently_cheats', 'statistics')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics', 'prefered')
	search_fields = ('username', 'owner__username', 'owner__first_name')
	ordering = ('username',)
	date_hierarchy = 'start_date'
	icon = '<i class="material-icons">person</i>'

@admin.register(DiscordGuild)
class DiscordGuildAdmin(admin.ModelAdmin):
	
	raw_id_fields = ("owner",)
	icon = """<img style="height: 48px; color: #00c6af;" src="/static/img/discord.svg"/>"""
