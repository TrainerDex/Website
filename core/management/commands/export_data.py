import io
import json
import zipfile

import pandas as pd
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from pokemongo.models import Trainer


class Command(BaseCommand):
    requires_migrations_checks = True

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("trainer_ids", nargs="+", type=int)

    def get_data(self, trainer: Trainer) -> io.BytesIO:
        file = io.BytesIO()
        zipfile_obj = zipfile.ZipFile(file, "w")  # Open zipfile in write mode

        updates = pd.DataFrame.from_records(trainer.update_set.all().values())

        # Add trainers JSON strings to zipfile with filename
        trainer_json = json.dumps(
            dict(
                uuid=str(trainer.uuid),
                start_date=trainer.start_date.isoformat(),
                faction=trainer.faction,
                last_cheated=trainer.last_cheated.isoformat() if trainer.last_cheated else None,
                statistics=trainer.statistics,
                daily_goal=trainer.daily_goal,
                total_goal=trainer.total_goal,
                trainer_code=trainer.trainer_code,
                country=str(trainer.country),
                verified=trainer.verified,
                event_10b=trainer.event_10b,
                event_1k_users=trainer.event_1k_users,
                legacy_40=trainer.legacy_40,
                nicknames=[
                    dict(
                        nickname=nickname.nickname,
                        active=nickname.active,
                    )
                    for nickname in trainer.nickname_set.all()
                ],
            ),
            indent=4,
        )
        zipfile_obj.writestr("trainer.json", trainer_json)

        # Save updates dataframe as CSV in-memory and add to zipfile with filename
        updates_csv = updates.to_csv(index=False, path_or_buf=None)
        zipfile_obj.writestr("updates.csv", updates_csv)

        zipfile_obj.close()  # Close the zipfile to finalize

        # Reset the file pointer to the beginning of the file for reading
        file.seek(0)

        # Now the zipfile is ready as an in-memory binary file, you can use it as needed
        # For example, you can return the zipfile object or retrieve the zip file as bytes using file.getvalue()

        return file

    def handle(self, *args, **options):
        if trainer_ids := options["trainer_ids"]:
            trainers = Trainer.objects.filter(id__in=trainer_ids)
        else:
            return

        for trainer in trainers:
            if trainer.owner.email:
                attachment = self.get_data(trainer)

                msg = EmailMessage(
                    "Data Export",
                    f"Hi {trainer.username},\n\nRecently you requested a data export in response to the news of TrainerDex shutting down.\nThankfully, TrainerDex is no longer shutting down, but here are your files anyway.\n\nHope you have a lovely day,\nJay and the rest of the TrainerDex team",
                    settings.DEFAULT_FROM_EMAIL,
                    [trainer.owner.email],
                )
                msg.attach(f"trainerdex_export_{trainer.uuid}.zip", attachment.getvalue(), "application/zip")
                msg.send()
