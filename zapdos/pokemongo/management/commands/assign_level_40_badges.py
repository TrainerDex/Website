from django.core.management.base import BaseCommand
from pokemongo.utils import set_legacy_40_badges


class Command(BaseCommand):
    help = "Assigns the Level 40 badges"

    def handle(self, *args, **options):
        trainers_assgined = set_legacy_40_badges()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully assigned the Level 40 badge to {} trainers".format(trainers_assgined)
            )
        )
