from django.contrib.gis import admin
from .models import Town


@admin.register(Town)
class UpdateAdmin(admin.OSMGeoAdmin):
	icon = '<i class="material-icons">location_on</i>'
