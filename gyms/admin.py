from django.contrib.gis import admin
from gyms.models import Town

admin.site.register(Town, admin.OSMGeoAdmin)
