from django.contrib.gis import admin
from .models import Town

admin.site.register(Town, admin.OSMGeoAdmin)
