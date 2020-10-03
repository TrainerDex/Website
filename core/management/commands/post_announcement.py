from datetime import datetime

import discord
import pytz
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation, timezone
from django.utils.translation import gettext as _
from dateutil.relativedelta import MO
from dateutil.rrule import rrule, WEEKLY
from humanize import precisedelta

from core.models import DiscordGuildSettings


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        key = settings.DISCORD_TOKEN
        current_time = timezone.now()
        rule = rrule(
            WEEKLY,
            dtstart=datetime(2016, 7, 4, 12, 0, tzinfo=pytz.utc),
            byweekday=MO,
        )
        deadline = rule.after(current_time)
        print("Starting Client")
        client = discord.Client()

        @client.event
        async def on_ready():
            for guild in client.guilds:
                if DiscordGuildSettings.objects.filter(id=guild.id).exists():
                    g: DiscordGuildSettings = DiscordGuildSettings.objects.get(id=guild.id)
                else:
                    continue

                translation.activate(g.language)

                if g.monthly_gains_channel:
                    channel = client.get_channel(g.monthly_gains_channel.id)
                    if channel:
                        if channel.permissions_for(guild.me).embed_links:
                            embed = discord.Embed(
                                title=_("Progress Deadline Reminder"),
                                description=_(
                                    "This is a reminder. The Progress Deadline is in {timedelta}."
                                ).format(
                                    timedelta=precisedelta(
                                        deadline - current_time,
                                        minimum_unit="hours",
                                        suppress=["seconds", "milliseconds", "microseconds"],
                                    )
                                ),
                                timestamp=deadline,
                                colour=13252437,
                            ).set_author(
                                name="TrainerDex",
                                url="https://www.trainerdex.co.uk/",
                                icon_url="https://www.trainerdex.co.uk/static/img/android-chrome-512x512.png",
                            )
                            await channel.send(embed=embed)
                        else:
                            message = _(
                                "This is a reminder. The Progress Deadline is in {timedelta}."
                            ).format(
                                timedelta=precisedelta(
                                    deadline - current_time,
                                    minimum_unit="hours",
                                    suppress=["seconds", "milliseconds", "microseconds"],
                                )
                            )
                            message += "\n\n"
                            message += deadline.astimezone(tz=pytz.timezone(g.timezone)).strftime(
                                "%Y %b %d %I:%M %p %Z"
                            )
                            await channel.send(message)

                translation.deactivate()

            await client.close()

        client.run(key)
