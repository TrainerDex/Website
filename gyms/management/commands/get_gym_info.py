from django.core.management.base import BaseCommand, CommandError
from gyms.models import Gym
import json

class Command(BaseCommand):
    help = 'Imports gym names, descriptions and images from pokemongomap json dump'

    def add_arguments(self, parser):
        parser.add_argument('file', type=open)

    def handle(self, *args, **options):
        mids = set()
        for line in options['file']:
            try:
                marker = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            if marker['mid'] in mids:
                continue
            mids.add(marker['mid'])
            #print(round(marker['position']['lat'], 5))
            try:
                gym = Gym.objects.get(
                    latitude=round(marker['position']['lat'], 6),
                    longitude=round(marker['position']['lng'], 6),
                )
                gym.name = marker['poketitle']
                gym.save()
            except Gym.DoesNotExist:
                pass
