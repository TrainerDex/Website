from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from teaproject.models import *

admin.site.register(Tea)
admin.site.register(Sweetener)
admin.site.register(Colour)

@admin.register(Cuppa)
class CuppaAdmin(admin.ModelAdmin):
	
	list_display = ('tea', 'colour', 'sweetener_amt', 'hardWater', 'isBought')
	search_fields = ('tea__name',)
	ordering = ('-datetime',)
	date_hierarchy = 'datetime'
