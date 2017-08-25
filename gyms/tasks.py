# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import periodic_task
from .monacle_scraper import MonacleScraper
from .search_indexes import GymIndex
from .models import Gym, Town
from config.es_client import es_client
from elasticsearch_dsl import Search
from django.db import transaction
from django.utils import timezone
from .serializers import ElasticGymSerializer
from elasticsearch.helpers import bulk
from django.forms.models import model_to_dict
from django.contrib.gis.geos import Point
import datetime
import random
import pytz
import requests
import humanize

# https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule
def isPointInPath(x, y, poly):
        num = len(poly)
        i = 0
        j = num - 1
        c = False
        for i in range(num):
                if  ((poly[i][1] > y) != (poly[j][1] > y)) and \
                        (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
                    c = not c
                j = i
        return c

@transaction.atomic
@periodic_task(
    run_every=datetime.timedelta(seconds=30),
    name="update_gyms",
    ignore_result=True
)
def update_gyms():
    m = MonacleScraper('https://kentpogomap.uk/raw_data', 'BIDoJSaHxR0Cz3mqJvI5kShtUc0CW/HPwK/CrRtEZhU=')
    boxes = (
        ((50.667801, -0.238047), (51.437802, 0.6463625)),
        ((50.667801, 0.6463625), (51.437802, 1.530762)),
    )
    gyms_for_es_update = []
    for box in boxes:
        spawns, pokestops, gyms = m.get_raw_data(
            box[0],
            box[1],
            pokestops=False,
            pokemon=False
        )
        
        for monacle_gym in gyms:
            try:
                gym = Gym.objects.get(id=monacle_gym.id)
            except Gym.DoesNotExist:
                gym = Gym()

            old_gym = model_to_dict(gym)
            gym.enabled = monacle_gym.enabled
            gym.guard_pokemon_id = monacle_gym.guard_pokemon_id
            gym.id = monacle_gym.id
            gym.last_modified = timezone.make_aware(monacle_gym.last_modified, pytz.utc) if monacle_gym.last_modified else None
            gym.last_scanned = timezone.make_aware(monacle_gym.last_scanned, pytz.utc) if monacle_gym.last_scanned else None
            gym.longitude = monacle_gym.location[1]
            gym.latitude = monacle_gym.location[0]
            gym.team = monacle_gym.team
            gym.slots_available = monacle_gym.slots_available

            if monacle_gym.name: # Monacle doesn't always return gym names, but we can at least allow them to be set by other methods
                gym.name = monacle_gym.name
            if monacle_gym.raid_pokemon:
                gym.raid_start = timezone.make_aware(monacle_gym.raid_start, pytz.utc) if monacle_gym.raid_start else None
                gym.raid_end = timezone.make_aware(monacle_gym.raid_end, pytz.utc) if monacle_gym.raid_end else None
                gym.raid_level = monacle_gym.raid_level
                gym.raid_pokemon_id = monacle_gym.raid_pokemon.id
                gym.raid_pokemon_name = monacle_gym.raid_pokemon.name
                gym.raid_pokemon_cp = monacle_gym.raid_pokemon.cp
                gym.raid_pokemon_move_1 = monacle_gym.raid_pokemon.move_1
                gym.raid_pokemon_move_2 = monacle_gym.raid_pokemon.move_2
            for town in Town.objects.all():
                point = Point(gym.longitude, gym.latitude)
                if point.intersects(town.poly):
                    gym.town = town
                    break
            if not gym.notification_sent_at:
                gym.notification_sent_at = timezone.now()
            if gym.town and gym.is_raid_active() and gym.notification_sent_at < gym.raid_start:
                gym.notification_sent_at = timezone.now()
                data = {
                    'embeds': [{
                        'title': '{} raid available'.format(gym.raid_pokemon_name),
                        'description': 'Ends at {} ({}) <@248080219586428929>'.format(gym.raid_end.strftime("%H:%M:%S"), humanize.naturaltime(timezone.now()-gym.raid_end)),
                        'url': 'https://www.google.com/maps/?daddr={},{}'.format(gym.latitude, gym.longitude),
                        'image': {
                            'url': 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom=15&size=250x125&maptype=roadmap&markers={0},{1}&key={2}'.format(gym.latitude, gym.longitude, 'AIzaSyCEadifeA8X02v2OKv-orZWm8nQf1Q2EZ4')
                        },
                        'thumbnail': {
                            'url': 'http://test.home.azelphur.com/img/pokemon/{:02d}.png'.format(gym.raid_pokemon_id)
                        }
                    }]
                }
                if hasattr(gym.town, 'discord_webhook') and gym.town.discord_webhook:
                    send_discord_webhook.delay(gym.town.discord_webhook, data)

            if old_gym != model_to_dict(gym):
                gym.save()
                gyms_for_es_update.append(gym)

        bulk(es_client, [ElasticGymSerializer(gym).es_instance().to_dict(include_meta=True) for gym in gyms_for_es_update])

@shared_task
def send_discord_webhook(url, data):
    r = requests.post(
        url,
        json=data
    )
    print(r.text)
