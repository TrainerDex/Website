from datetime import datetime

import discord
import pytz
from core.models import DiscordGuildSettings
from dateutil.relativedelta import MO
from dateutil.rrule import WEEKLY, rrule
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from humanize import precisedelta


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
        self.stdout.write(self.style.NOTICE("Starting Client"))
        intents = discord.Intents(guilds=True, guild_messages=True)
        client = discord.Client(
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=True, users=False, roles=True),
        )

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
                                        minimum_unit="minutes",
                                        suppress=[
                                            "seconds",
                                            "milliseconds",
                                            "microseconds",
                                        ],
                                    )
                                ),
                                timestamp=deadline,
                                colour=13252437,
                            ).set_author(
                                name="TrainerDex",
                                url="https://trainerdex.app/",
                                icon_url="https://trainerdex.app/static/img/android-chrome-512x512.png",
                            )
                            await channel.send(embed=embed)
                        else:
                            message = _(
                                "This is a reminder. The Progress Deadline is in {timedelta}."
                            ).format(
                                timedelta=precisedelta(
                                    deadline - current_time,
                                    minimum_unit="minutes",
                                    suppress=[
                                        "seconds",
                                        "milliseconds",
                                        "microseconds",
                                    ],
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
