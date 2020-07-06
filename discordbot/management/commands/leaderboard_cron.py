from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
import discord
from core.models import DiscordGuild, DiscordGuildMembership
from datetime import datetime
from dateutil.tz import tzutc
from dateutil.relativedelta import relativedelta, MO
from discordbot import __version__ as VERSION
from humanize import naturaldate
from humanfriendly import format_number, format_timespan
from pokemongo.models import Trainer, Update
from pokemongo.shortcuts import filter_leaderboard_qs
from time import time

class Command(BaseCommand):
    help = 'Runs the weekly gains leaderboards.'
    
    def add_arguments(self, parser):
        parser.add_argument('site', nargs=1, type=str)
        parser.add_argument('guild', nargs=1, type=int)
    
    def handle(self, *args, **options):
        print('Finding Client Key')
        try:
            key = Site.objects.get(domain=options['site'][0]).socialapp_set.filter(provider='discord').first().key
        except:
            raise CommandError("Can't find key for site '{}'".format(options['site'][0]))
        
        print('Generating Client')
        client = discord.Client(
            status=discord.Status('online'),
        )
        
        @client.event
        async def on_ready():
            guilddb = DiscordGuild.objects.get(id=options['guild'][0])
            channel = client.get_channel(guilddb.discordguildsettings.monthly_gains_channel.id)
            guilddb.refresh_from_api()
            guilddb.sync_roles()
            guilddb.sync_members()
            _unfiltered_members = DiscordGuildMembership.objects.filter(active=True, guild=guilddb)
            _unfiltered_members = [x for x in _unfiltered_members if 'NoLB' not in (y.name for y in x.roles)]
            mbrs = filter_leaderboard_qs(Trainer.objects.filter(owner__socialaccount__discordguildmembership__in=_unfiltered_members))
            
            print("Getting the latest Monday gone by", end='')
            last_monday = datetime.utcnow()
            print(":", last_monday)
            
            print("Getting frequency", end='')
            frequency = 'WEEKLY' # Yes this is hardcoded, sue me. It'll change soon.
            print(":", frequency)
            
            print("Getting comparison date", end='')
            if frequency=='WEEKLY':
                this_month = last_monday
                last_month = this_month+relativedelta(weeks=-1)
                print(":", this_month, last_month, this_month-last_month)
            
            print('Loading updates on latest date', end='')
            this_months_submissions = Update.objects.filter(trainer__in=mbrs, update_time__lte=this_month, update_time__gt=this_month+relativedelta(weeks=-1)).order_by('trainer', '-update_time').distinct('trainer')
            print(":", this_months_submissions.count())
            
            print('Loading updates on latest date', end='')
            last_months_submissions = Update.objects.filter(trainer__in=mbrs, update_time__lte=last_month, update_time__gt=last_month+relativedelta(weeks=-1)).order_by('trainer', '-update_time').distinct('trainer')
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
            
            leaderboard_text="WEEKLY GAINS LEADERBOARD for {}:\n\n".format(guilddb.name)
            for a,b in enumerate(gains_list):
                leaderboard_text+="#{pos} **{trainer}** gained {gain}! (_{old_xp}⇒{new_xp}_, _{old_date}⇒{new_date}_, **{delta}**)\n".format(pos=a+1, trainer=b['trainer'].nickname, gain=format_number(b['gain']), old_xp=format_number(b['old'].total_xp), new_xp=format_number(b['new'].total_xp), delta=format_timespan(b['delta'], max_units=2), old_date=naturaldate(b['old'].update_time), new_date=naturaldate(b['new'].update_time))
            
            if new_entries.count() > 0:
                leaderboard_text+="\n\nWe have **{x}** new entries who may be ranked next week, including; _{top_5}_".format(x=new_entries.count(), top_5=", ".join([x.trainer.nickname for x in sorted(new_entries, key=lambda x: x.total_xp, reverse=True)[:5]]))
            if new_entries.count() > 5:
                leaderboard_text+="…"
            if dropped_trainers.count() > 0:
                leaderboard_text+="\n**{x}** trainers didn't submit in time this week so couldn't be ranked, including; _{top_5}_".format(x=dropped_trainers.count(), top_5=", ".join([x.trainer.nickname for x in dropped_trainers[:5]]))
            if dropped_trainers.count() > 5:
                leaderboard_text+="…"
            leaderboard_text+="\n\nDon't forget to submit in time, the weekly gains deadline is Monday 12:00-noon UTC. Don't leave it to last minute though, you can submit any time during the week!\n_Support or suggestions? Contact us on Twitter @TrainerDexApp_"
            print(leaderboard_text)
            
            print("Splitting and sending message")
            message = ""
            message_parts = []
            for part in leaderboard_text.split('\n'):
                if len(message+part+"\n") > 2000:
                    message_parts.append(message)
                    message = part+"\n"
                else:
                    message+=part+"\n"
            message_parts.append(message)
            del message
            
            base_nonce = str(int(time()))
            for nonce, message in enumerate(message_parts):
                print("message:", message)
                print("nonce:", int(base_nonce+str(nonce)))
                msg = await channel.send(message, nonce=int(base_nonce+str(nonce)))
                await msg.pin()
            
            await client.close()
            
        print('Running verion', VERSION)
        client.run(key)
