from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
import discord
from discordbot import __version__ as VERSION
from discord.ext.commands import Bot
from discordbot.welcome import Welcomer

class Command(BaseCommand):
    help = 'Starts a Discord.py bot'
    
    def add_arguments(self, parser):
        parser.add_argument('site', nargs=1, type=str)
    
    def handle(self, *args, **options):
        print('Finding Client Key')
        try:
            key = Site.objects.get(domain=options['site'][0]).socialapp_set.filter(provider='discord').first().key
        except:
            raise CommandError("Can't find key for site '{}'".format(options['site'][0]))
        
        print('Building bot verion', VERSION)
        bot = Bot(
        command_prefix=['tdx!','.'],
        case_insensitive=True,
        description="Welcome to TrainerDex. I am the rewrite of the new bot. Call me discordbot2 for short. The name isn't very creative but what are you going to do.",
        owner_ids=[319792326958514176,319844458558390274],
        activity=discord.Game(VERSION)
        )
        print('Running verion', VERSION)
        print('Initiating Cogs')
        bot.add_cog(Welcomer(bot))
        print('Starting Bot')
        bot.run(key)
