import os
import discord
from discord import app_commands
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
command_prefix = '%'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
client = commands.Bot(command_prefix=command_prefix, intents=intents)
# tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Run the client
client.run(ACCESS_TOKEN)
