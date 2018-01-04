from django import forms
from django.contrib import admin
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from trainer.models import *

admin.site.register(Faction)
admin.site.register(PlayZonesDetailCountry)
admin.site.register(PlayZonesDetailRegion)
admin.site.register(PlayZonesDetailSubregion)
admin.site.register(PlayZonesDetailCity)

@admin.register(Update)
class UpdateAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Update, {
		'trainer' : 'trainer'
	})
	list_display = ('trainer', 'xp', 'update_time')
	search_fields = ('trainer__username', 'trainer__owner__username')
	ordering = ('-update_time',)
	date_hierarchy = 'update_time'

@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'username' : 'user'
	})
	list_display = ('username', 'faction', 'currently_cheats', 'statistics')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics')
	search_fields = ('username', 'owner__username', 'owner__first_name')
	ordering = ('username',)
	date_hierarchy = 'start_date'
