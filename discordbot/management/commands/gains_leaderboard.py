from datetime import datetime
from typing import Iterable, List

import discord
from django.conf import settings
from django.core.management.base import BaseCommand
from dateutil.relativedelta import MO
from dateutil.rrule import rrule, WEEKLY
from humanize import naturaldate
from humanfriendly import format_number, format_timespan

from core.models import DiscordGuild
from pokemongo.models import Trainer, Update
from pokemongo.shortcuts import filter_leaderboard_qs


class Gain:
    def __init__(self, *args, **kwargs):
        self.trainer = kwargs.get("trainer")
        self.this_week = kwargs.get("this_week")
        self.last_week = kwargs.get("last_week")
        self.stat = kwargs.get("stat", "total_xp")

    @property
    def this_week_stat(self):
        return getattr(self.this_week, self.stat)

    @property
    def last_week_stat(self):
        return getattr(self.last_week, self.stat)

    @property
    def stat_delta(self):
        return self.this_week_stat - self.last_week_stat

    @property
    def time_delta(self):
        return self.this_week.update_time - self.last_week.update_time

    @property
    def days(self):
        return max(round(self.time_delta.total_seconds() / 86400), 1)

    @property
    def rate(self):
        return self.stat_delta / self.days


class Command(BaseCommand):
    help = "Runs the weekly gains leaderboards."

    def handle(self, *args, **options):
        key = settings.DISCORD_TOKEN
        current_time = datetime.utcnow()
        rule = rrule(WEEKLY, dtstart=datetime(2016, 7, 4, 12, 0), byweekday=MO,)
        next_week = (rule.before(current_time, inc=True), rule.after(current_time))
        this_week = (rule.before(next_week[0]), next_week[0])
        last_week = (rule.before(this_week[0]), this_week[0])
        week_number = this_week[0].isocalendar()[:2]

        print("Starting Client")
        client = discord.Client(fetch_offline_members=True)

        async def generate_leaderboard(guild: discord.Guild) -> DiscordGuild:
            ex_roles: List[discord.Roles] = [
                x for x in guild.roles if x.name in ("NoLB", "TrainerDex Exclude")
            ]
            members: List[discord.Members] = [
                x for x in guild.members if not bool(set(x.roles) & set(ex_roles))
            ]

            trainers: Iterable[Trainer] = filter_leaderboard_qs(
                Trainer.objects.filter(
                    owner__socialaccount__uid__in=[x.id for x in members],
                    owner__socialaccount__provider="discord",
                )
            )

            this_weeks_submissions: Iterable[Update] = (
                Update.objects.filter(
                    trainer__in=trainers,
                    update_time__gte=this_week[0],
                    update_time__lt=this_week[1],
                )
                .order_by("trainer", "-update_time")
                .distinct("trainer")
            )
            last_weeks_submissions: Iterable[Update] = (
                Update.objects.filter(
                    trainer__in=trainers,
                    update_time__gte=last_week[0],
                    update_time__lt=last_week[1],
                )
                .order_by("trainer", "-update_time")
                .distinct("trainer")
            )

            eligible_entries: Iterable[Update] = this_weeks_submissions.filter(
                trainer__in=last_weeks_submissions.values_list("trainer", flat=True)
            )
            gains = [
                Gain(
                    trainer=x.trainer,
                    this_week=x,
                    last_week=last_weeks_submissions.get(trainer=x.trainer),
                    stat="total_xp",
                )
                for x in eligible_entries
            ]
            gains.sort(key=lambda x: x.rate, reverse=True)

            new_entries: List[Trainer] = [
                x.trainer
                for x in this_weeks_submissions.exclude(
                    trainer__in=last_weeks_submissions.values_list("trainer", flat=True)
                )
            ]

            dropped_trainers: List[Trainer] = [
                x.trainer
                for x in last_weeks_submissions.exclude(
                    trainer__in=this_weeks_submissions.values_list("trainer", flat=True)
                )
            ]

            return (gains, new_entries, dropped_trainers)

        async def format_leaderboard_as_text(
            guild: discord.Guild,
            gains: List[Gain],
            new_entries: List[Trainer],
            dropped_trainers: List[Trainer],
            deadline: datetime,
        ):
            title = "Weekly Gains Leaderboard for {guild.name}".format(guild=guild)
            ranked = [
                "#{position} **{trainer}**"
                " (Rate: {rate}, Interval: {interval}, Gain: {then} ⇒ {now} (+{delta}))".format(
                    position=position,
                    trainer=entry.trainer,
                    rate=format_number(round(entry.rate)),
                    interval=format_timespan(entry.time_delta, max_units=2),
                    then=format_number(entry.last_week_stat),
                    now=format_number(entry.this_week_stat),
                    delta=format_number(entry.stat_delta),
                )
                for position, entry in enumerate(gains)
            ]

            return """**{title}**

{ranked}

**{new_count}** New entries: {new}
**{lost_count}** Lost entries: {lost}

Next weeks deadline is: {deadline}
""".format(
                title=title,
                ranked="\n".join(ranked),
                new=", ".join([str(x) for x in new_entries]),
                lost=", ".join([str(x) for x in dropped_trainers]),
                new_count=format_number(len(new_entries)),
                lost_count=format_number(len(dropped_trainers)),
                deadline=naturaldate(deadline),
            )

        async def gen_and_print(guild: discord.Guild, deadline: datetime):
            gains, new_entries, dropped_trainers = await generate_leaderboard(guild)
            text = await format_leaderboard_as_text(
                guild, gains, new_entries, dropped_trainers, deadline
            )
            print(text)

        @client.event
        async def on_ready():
            for guild in client.guilds:

                await gen_and_print(guild, next_week[1])

            # g: DiscordGuild = DiscordGuild.objects.get(id=guild.id)
            # channel: discord.Channel = client.get_channel(
            # g.discordguildsettings.monthly_gains_channel.id
            # )

            # print("Splitting and sending message")
            # message = ""
            # message_parts = []
            # for part in leaderboard_text.split("\n"):
            #     if len(message + part + "\n") > 2000:
            #         message_parts.append(message)
            #         message = part + "\n"
            #     else:
            #         message += part + "\n"
            # message_parts.append(message)
            # del message
            #
            # for message in message_parts:
            #     msg = await channel.send(message)
            #     await msg.pin()

            await client.close()

        client.run(key)
