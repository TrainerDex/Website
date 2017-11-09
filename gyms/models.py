#from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.gis.db import models
from timezone_field import TimeZoneField
from django.core.validators import validate_comma_separated_integer_list
from trainer.models import Faction

class Town(models.Model):
    name = models.CharField(max_length=64)
    poly = models.PolygonField()
    gym_discord_webhook_url = models.URLField(null=True, blank=True)
    pokemon_discord_webhook_url = models.URLField(null=True, blank=True)
    include_pokemon = models.CharField(max_length=1024, validators=[validate_comma_separated_integer_list], null=True, blank=True)
    exclude_pokemon = models.CharField(max_length=1024, validators=[validate_comma_separated_integer_list], null=True, blank=True)
    timezone = TimeZoneField(default='Europe/London')

    def __str__(self):
        return self.name


class Gym(models.Model):
    enabled = models.BooleanField()
    guard_pokemon_id = models.IntegerField(null=True, blank=True)
    id = models.CharField(max_length=64, primary_key=True)
    last_modified = models.DateTimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    name = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    
    team = models.ForeignKey(Faction, on_delete=models.SET_DEFAULT, default=0)
    slots_available = models.IntegerField()
    raid_start = models.DateTimeField(null=True, blank=True)
    raid_end = models.DateTimeField(null=True, blank=True)
    raid_level = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)],
                                     null=True, blank=True)
    raid_pokemon_id = models.PositiveIntegerField(null=True, blank=True)
    raid_pokemon_name = models.CharField(max_length=64, null=True, blank=True)
    raid_pokemon_cp = models.PositiveIntegerField(null=True, blank=True)
    raid_pokemon_move_1 = models.PositiveIntegerField(null=True, blank=True)
    raid_pokemon_move_2 = models.PositiveIntegerField(null=True, blank=True)
    notification_sent_at = models.DateTimeField()
    town = models.ForeignKey(Town, null=True, blank=True)

    def is_raid_active(self):
        if self.raid_start and self.raid_end and timezone.now() >= self.raid_start and timezone.now() <= self.raid_end:
            return True
        return False
