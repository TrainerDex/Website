from discord.ext import commands
from async_crom.job import CromJob
from async_cron.schedule import Scheduler

class Leaderboard(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
    
