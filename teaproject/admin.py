from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add
from teaproject.models import *

admin.site.register(Tea)
admin.site.register(Sweetener)
admin.site.register(Colour)

@admin.register(Cuppa)
class CuppaAdmin(AjaxSelectAdmin):
	
	list_display = ('tea', 'colour', 'sweetener_amt', 'hardWater', 'isBought')
	search_fields = ('tea__name',)
	ordering = ('-datetime',)
	date_hierarchy = 'datetime'
	icon = '<i class="material-icons">☕</i>'
	
