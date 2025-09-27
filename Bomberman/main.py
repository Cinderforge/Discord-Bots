import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
import json
import shutil

# Get environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv('TOKEN')

# Create logging file
log_handler = logging.FileHandler(filename='./discord.log', encoding='utf-8', mode='w')

# Set the intents and create the bot
command_prefix = '$'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
client = commands.Bot(command_prefix=command_prefix, intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.command(name='config')
async def config(ctx, *args):
    data = {}
    roles = ctx.message.raw_role_mentions
    data['bomber'] = roles[0]

    dirpath = os.path.join('guild_data', str(ctx.guild.id))
    os.makedirs(dirpath, exist_ok=True)
    with open('guild_data/' + str(ctx.guild.id) + '/settings.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.send('Watching bombers 💣💣💣💣!')

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return
    try:
        with open('guild_data/' + str(message.guild.id) + '/settings.json', 'r') as f:
            data = json.load(f)
            role = data['bomber']
    except FileNotFoundError:
        return
    if discord.utils.get(message.author.roles, id=role) != None:
        await message.add_reaction('💣')

# Run the client
client.run(ACCESS_TOKEN)
