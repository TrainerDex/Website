# from datetime import date, datetime
# from typing import Iterable, List, Union

# import discord
# from dateutil.relativedelta import MO
# from dateutil.rrule import WEEKLY, rrule
# from django.conf import settings
# from django.core.management.base import BaseCommand
# from django.db.models import F
# from django.utils import timezone, translation
# from django.utils.translation import gettext as _
# from django.utils.translation import pgettext
# from humanize import intcomma

# from core.models.discord import DiscordGuild
# from pokemongo.models import Trainer, Update
# from pokemongo.shortcuts import filter_leaderboard_qs, filter_leaderboard_qs__update


# class Entry:
#     def __init__(self, *args, **kwargs):
#         self.trainer = kwargs.get("trainer")
#         self.this_week = kwargs.get("this_week")
#         self.last_week = kwargs.get("last_week")
#         self.stat = kwargs.get("stat", "total_xp")

#     @property
#     def this_week_stat(self):
#         return getattr(self.this_week, self.stat)

#     @property
#     def last_week_stat(self):
#         if self.last_week:
#             return getattr(self.last_week, self.stat)

#     @property
#     def stat_delta(self):
#         if self.last_week:
#             return self.this_week_stat - self.last_week_stat

#     @property
#     def time_delta(self):
#         if self.last_week:
#             return self.this_week.update_time - self.last_week.update_time

#     @property
#     def days(self):
#         if self.last_week:
#             return max(round(self.time_delta.total_seconds() / 86400), 1)

#     @property
#     def rate(self):
#         if self.last_week:
#             return self.stat_delta / self.days


# class Command(BaseCommand):
#     help = "Runs the weekly gains leaderboards."

#     # def add_arguments(self, parser):
#     #     parser.add_argument("stat", default="total_xp")

#     def handle(self, *args, **kwargs):
#         key = settings.DISCORD_TOKEN
#         current_time = timezone.now()
#         # stat = kwargs.get("stat", "total_xp")
#         stat = "gymbadges_gold"
#         rule = rrule(
#             WEEKLY,
#             dtstart=datetime(2016, 7, 4, 12, 0, tzinfo=timezone.utc),
#             byweekday=MO,
#         )
#         if current_time.date() == date(2020, 11, 30):
#             next_week = (
#                 datetime(2020, 11, 30, 12, 0, tzinfo=timezone.utc),
#                 datetime(2020, 12, 7, 12, 0, tzinfo=timezone.utc),
#             )
#             this_week = (
#                 datetime(2020, 11, 22, 20, 0, tzinfo=timezone.utc),
#                 datetime(2020, 11, 30, 12, 0, tzinfo=timezone.utc),
#             )
#             last_week = (
#                 datetime(2020, 11, 15, 20, 0, tzinfo=timezone.utc),
#                 datetime(2020, 11, 22, 20, 0, tzinfo=timezone.utc),
#             )
#             week_number = (2020, 48)
#         else:
#             next_week = (rule.before(current_time, inc=True), rule.after(current_time))
#             this_week = (rule.before(next_week[0]), next_week[0])
#             last_week = (rule.before(this_week[0]), this_week[0])
#             week_number = this_week[0].isocalendar()[:2]

#         print(next_week, this_week, last_week, week_number, stat)
#         self.stdout.write(self.style.NOTICE("Starting Client"))
#         intents = discord.Intents(
#             guilds=True,
#             members=True,
#             emojis=True,
#             guild_messages=True,
#             guild_typing=True,
#         )
#         client = discord.Client(intents=intents, allowed_mentions=discord.AllowedMentions.none())

#         async def generate_leaderboard(
#             guild: discord.Guild,
#             stat: str,
#         ) -> Iterable[Union[List[Entry], List[Trainer]]]:
#             ex_roles: List[discord.Roles] = [
#                 x for x in guild.roles if x.name in ("NoLB", "TrainerDex Exclude")
#             ]
#             members: List[discord.Members] = [
#                 x for x in guild.members if not bool(set(x.roles) & set(ex_roles))
#             ]

#             trainers: Iterable[Trainer] = filter_leaderboard_qs(
#                 Trainer.objects.filter(
#                     owner__socialaccount__uid__in=[x.id for x in members],
#                     owner__socialaccount__provider="discord",
#                 )
#             )

#             this_weeks_submissions: Iterable[Update] = filter_leaderboard_qs__update(
#                 Update.objects.filter(
#                     trainer__in=trainers,
#                     update_time__lt=this_week[1],
#                 )
#                 .annotate(value=F(stat))
#                 .exclude(value__isnull=True)
#                 .order_by("trainer", "-update_time")
#                 .distinct("trainer")
#             )
#             last_weeks_submissions: Iterable[Update] = filter_leaderboard_qs__update(
#                 Update.objects.filter(
#                     trainer__in=trainers,
#                     update_time__lt=last_week[1],
#                 )
#                 .annotate(value=F(stat))
#                 .exclude(value__isnull=True)
#                 .order_by("trainer", "-update_time")
#                 .distinct("trainer")
#             )

#             entries = [
#                 (
#                     Entry(
#                         trainer=x.trainer,
#                         this_week=x,
#                         last_week=last_weeks_submissions.get(trainer=x.trainer),
#                         stat=stat,
#                     )
#                     if last_weeks_submissions.filter(trainer=x.trainer).exists()
#                     else Entry(trainer=x.trainer, this_week=x, last_week=None, stat=stat)
#                 )
#                 for x in this_weeks_submissions
#             ]
#             entries.sort(key=lambda x: x.this_week_stat, reverse=True)

#             return entries

#         async def format_leaderboard_as_text(
#             guild: discord.Guild,
#             entries: List[Entry],
#             deadline: datetime,
#             stat: str,
#         ):
#             emoji = {
#                 "teamless": client.get_emoji(743873748029145209),
#                 "mystic": client.get_emoji(430113444558274560),
#                 "valor": client.get_emoji(430113457149575168),
#                 "instinct": client.get_emoji(430113431333371924),
#                 "travel_km": client.get_emoji(743122298126467144),
#                 "badge_travel_km": client.get_emoji(743122298126467144),
#                 "capture_total": client.get_emoji(743122649529450566),
#                 "badge_capture_total": client.get_emoji(743122649529450566),
#                 "pokestops_visited": client.get_emoji(743122864303243355),
#                 "badge_pokestops_visited": client.get_emoji(743122864303243355),
#                 "total_xp": client.get_emoji(743121748630831165),
#                 "gymbadges_gold": client.get_emoji(743853262469333042),
#                 "number": "#",
#             }
#             verbose_names = {
#                 "teamless": pgettext("team_name_team0", "No Team"),
#                 "mystic": pgettext("team_name_team1", "Team Mystic"),
#                 "valor": pgettext("team_name_team2", "Team Valor"),
#                 "instinct": pgettext("team_name_team3", "Team Instinct"),
#                 "badge_travel_km": pgettext("badge_travel_km_title", "Jogger"),
#                 "badge_capture_total": pgettext("badge_capture_total_title", "Collector"),
#                 "badge_pokestops_visited": pgettext("badge_pokestops_visited_title", "Backpacker"),
#                 "total_xp": pgettext("profile_total_xp", "Total XP"),
#                 "gymbadges_gold": pgettext("gymbadges_gold", "Gold Gyms"),
#             }

#             title = _(
#                 "Weekly {stat_emoji} {stat_name} Totals Leaderboard for \N{BUSTS IN SILHOUETTE} _{guild.name}_"
#             ).format(
#                 stat_emoji=emoji.get(stat, ""),
#                 stat_name=verbose_names.get(stat, stat),
#                 guild=guild,
#             )

#             if not entries:
#                 return

#             ranked = [
#                 _("#{position} **{trainer}** {stat} (+{delta})").format(
#                     position=position + 1,
#                     trainer=entry.trainer,
#                     delta=intcomma(entry.stat_delta),
#                     stat=intcomma(entry.this_week_stat),
#                 )
#                 if (entry.last_week and entry.this_week_stat != entry.last_week_stat)
#                 else _("#{position} **{trainer}** {stat}").format(
#                     position=position + 1,
#                     trainer=entry.trainer,
#                     stat=intcomma(entry.this_week_stat),
#                 )
#                 for position, entry in enumerate(entries)
#             ]

#             return """**{title}**
# Week: `{year}W{week}` Deadline: `{this_week_deadline} UTC`

# {ranked}

# It's all manual atm, sorry!
# **Next weeks deadline is: `{deadline} UTC`**
# """.format(
#                 title=title,
#                 year=week_number[0],
#                 week=week_number[1],
#                 this_week_deadline=this_week[1],
#                 ranked="\n".join(ranked),
#                 deadline=deadline,
#             )

#         @client.event
#         async def on_ready():
#             ek_pogo = client.get_guild(319811219093716993)
#             guilds = [ek_pogo]
#             for guild in guilds:
#                 if DiscordGuild.objects.filter(id=guild.id).exists():
#                     g: DiscordGuild = DiscordGuild.objects.get(id=guild.id)
#                 else:
#                     continue

#                 translation.activate(g.language)

#                 if guild is ek_pogo:
#                     channel = client.get_channel(608770319552872452)
#                     if channel:
#                         async with channel.typing():
#                             entries = await generate_leaderboard(guild, stat)
#                             text = await format_leaderboard_as_text(
#                                 guild,
#                                 entries,
#                                 next_week[1],
#                                 stat,
#                             )

#                             message = ""
#                             message_parts = []
#                             for part in text.split("\n"):
#                                 if len(message + part + "\n") > 2000:
#                                     message_parts.append(message)
#                                     message = part + "\n"
#                                 else:
#                                     message += part + "\n"
#                             message_parts.append(message)

#                             for x in message_parts:
#                                 await channel.send(x)
#                                 # print(x)

#                 translation.deactivate()

#             await client.close()

#         client.run(key)
