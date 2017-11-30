from django.contrib.gis import admin
from gyms.models import Town, Gym

admin.site.register(Town, admin.OSMGeoAdmin)
