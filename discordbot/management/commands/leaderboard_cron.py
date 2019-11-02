from django.core.management.base import BaseCommand, CommandError
import discord
from core.models import DiscordGuild
from datetime import datetime, date
from dateutil.tz import tzutc
from dateutil.relativedelta import relativedelta, MO
from discordbot import __version__ as VERSION
from humanize import naturaldate
from humanfriendly import format_number, format_timespan
from pokemongo.models import Trainer, Update

class Command(BaseCommand):
    help = 'Runs the weekly/monthly gains leaderboards.'
    
    def add_arguments(self, parser):
        parser.add_argument('token', nargs=1, type=str)
        parser.add_argument('guild', nargs=1, type=int)
    
    def handle(self, *args, **options):
        print('Generating Client')
        client = discord.Client(
            status=discord.Status('online'),
        )
        
        @client.event
        async def on_ready():
            guilddb = DiscordGuild.objects.get(id=options['guild'][0])
            channel = client.get_channel(guilddb.options_xp_gains_channel.id)
            # guilddb.refresh_from_api()
            guilddb.sync_members()
            mbrs = Trainer.objects.filter(owner__socialaccount__discordguildmembership__guild=guilddb, owner__socialaccount__discordguildmembership__active=True)
            
            # Get members
            # Get updates by members filtered by the last "month"
            # Get updates by members as above ... offset by the last month
            # For members in both lists, calculate differences
            # For memebers only in latest list, welcome to leaderboard
            # For members only in older list, apologise for loss of rank
            
            print("Getting the latest Monday gone by", end='')
            last_monday = datetime.now(tzutc())-relativedelta(weekday=MO(-1), hour=23, minute=59, second=59, microsecond=999999)
            print(":", last_monday)
            
            print("Getting frequency", end='')
            frequency = 'MONTHLY' # Yes this is hardcoded, sue me. It'll change soon.
            print(":", frequency)
            
            print("Getting comparison date", end='')
            if frequency=='MONTHLY':
                this_month = last_monday
                last_month = this_month+relativedelta(months=-1, day=31, weekday=MO(-1))
                month_b4_last = last_month+relativedelta(months=-1, day=31, weekday=MO(-1))
                print(":", this_month, last_month, this_month-last_month)
            
            print('Loading updates on latest date', end='')
            this_months_submissions = Update.objects.filter(trainer__in=mbrs, update_time__lte=this_month, update_time__gt=last_month).order_by('trainer', '-update_time').distinct('trainer')
            print(":", this_months_submissions.count())
            
            print('Loading updates on latest date', end='')
            last_months_submissions = Update.objects.filter(trainer__in=mbrs, update_time__lte=last_month, update_time__gt=month_b4_last).order_by('trainer', '-update_time').distinct('trainer')
            print(":", last_months_submissions.count())
            
            print('Generating lists')
            eligible_entries = this_months_submissions.filter(trainer__in=last_months_submissions.values_list('trainer', flat=True))
            print("Eligible Entries: ", eligible_entries.count())
            new_entries = this_months_submissions.exclude(trainer__in=last_months_submissions.values_list('trainer', flat=True))
            print("New Entries: ", new_entries.count())
            dropped_trainers = last_months_submissions.exclude(trainer__in=this_months_submissions.values_list('trainer', flat=True))
            print("Dropped Trainers: ", dropped_trainers.count())
            
            gains_list = []
            for entry in eligible_entries:
                gains_list.append({
                    'trainer': entry.trainer,
                    'new': entry,
                    'old': last_months_submissions.get(trainer=entry.trainer),
                    'gain': entry.total_xp-last_months_submissions.get(trainer=entry.trainer).total_xp,
                    'delta': entry.update_time.date()-last_months_submissions.get(trainer=entry.trainer).update_time.date(),
                })
            gains_list.sort(key=lambda x: x['new'].total_xp-x['old'].total_xp, reverse=True)
            
            leaderboard_text="GAINS LEADERBOARD:\n\n"
            for a,b in enumerate(gains_list):
                leaderboard_text+="#{pos} **{trainer}** gained {gain}! (_{old_xp}⇒{new_xp}_, _{old_date}⇒{new_date}_, **{delta}**)\n".format(pos=a+1, trainer=b['trainer'].nickname, gain=format_number(b['gain']), old_xp=format_number(b['old'].total_xp), new_xp=format_number(b['new'].total_xp), delta=format_timespan(b['delta'], max_units=2), old_date=naturaldate(b['old'].update_time), new_date=naturaldate(b['new'].update_time))
            
            leaderboard_text+="\n\nWe have **{x}** new entries who will be ranked next month, including; _{top_5}_…".format(x=new_entries.count(), top_5=", ".join([x.trainer.nickname for x in sorted(new_entries, key=lambda x: x.total_xp, reverse=True)[:5]]))
            leaderboard_text+="\n**{x}** trainers didn't submit in time this month so couldn't be ranked, including; _{top_5}_…".format(x=dropped_trainers.count(), top_5=", ".join([x.trainer.nickname for x in dropped_trainers[:5]]))
            print(leaderboard_text)
            await channel.send(leaderboard_text)
            
            await client.close()
            
        print('Running verion', VERSION)
        client.run(options['token'][0])
