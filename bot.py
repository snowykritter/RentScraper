import discord
from discord import role
from discord import member
from discord.colour import Color
from discord.ext import commands
import random
import json
from datetime import datetime

# import token from json file
with open('egg.json') as cracked_egg:
    keys = json.loads(cracked_egg.read())

# settings
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guild_reactions = True


# initialize bot
client = commands.Bot(command_prefix=">", intents=intents)

# global variables
datenow=datetime.now()
month=datenow.month
day=datenow.day
year=datenow.year


@client.event
async def on_ready():
    print('ready')
    await client.change_presence(status = discord.Status.do_not_disturb, activity = discord.Game('finding rent!'))

@client.command()
async def test(ctx):
    await ctx.send(f'toad')

token = keys['token']
client.run(token)
