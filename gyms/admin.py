from django.contrib.gis import admin
from gyms.models import Town, Gym

class TownAdmin(admin.OSMGeoAdmin):
	icon = '<i class="material-icons">🏙️</i>'

admin.site.register(Town, TownAdmin)

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
	icon = '<i class="material-icons">warning</i>'
