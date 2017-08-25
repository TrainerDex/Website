from django.contrib.gis import admin
from .models import Town
# Register your models here.
admin.site.register(Town, admin.OSMGeoAdmin)
