from itertools import count
import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')
COLOR = int(os.getenv('COLOR'), 16)

intents = discord.Intents.default()
intents.message_content = True  # also enable this in the Developer Portal
bot = commands.Bot(command_prefix='$', intents=intents)

class player():
    def __init__(self, player, health): 
        self.player = player
        self.health = health
        self.health, self.hand, self.hidden, self.tarot, self.psum, self.hsum= 0 , [], [], [], 0, 0
    def sum(self):
        self.psum = sum(self.hand)
        self.hsum = sum(self.hidden)


class game():
    p1deck = []
    p2deck = [] 
    p1hidden = []
    p2hidden = []
    currenplayer = player  
    goal = 21
    gameEmbed = discord.Embed
    turn = 1
    currenbet = 1
    standcount = 0
    deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def draw(self, player, amount):
        if player.psum > self.goal:
            print("Busted! You may not draw a card")
            print(self.goal)
        else: 
            if len(self.deck) > 0:
                for _ in range(amount):
                    drawn = random.choice(self.deck)
                    player.hand.append(drawn)
                    if len(player.hidden) > 1:
                        player.hidden.append(0)
                    else:
                        player.hidden.append(drawn)
                    self.deck.remove(drawn)
            else:
                print("Empty deck!")
        player.sum()
    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Bluff Challenge",
            description=str(f"Bust Limit: {self.goal}"),
            color=COLOR
        )
        embed.add_field(name=f"{self.p1.player} HP {self.p1.health}", value=self.p1.hand, inline=True)
        embed.add_field(name=f"{self.p2.player} HP {self.p2.health}", value=self.p2.hand, inline=True)
        embed.add_field(name="\u000b", value="\u000b", inline=False)
        embed.add_field(name="Hand", value=self.p1.hidden, inline=True)
        embed.add_field(name="Hand", value=self.p2.hidden, inline=True)
        embed.set_footer(text=f"Turn {self.turn} | Bet {self.currenbet} | {self.currenplayer.player}'s turn")
        return embed
    def fool(self):
        for i in self.currenplayer.hand:
            self.deck.append(i)
        self.currenplayer.hand = []
        self.currenplayer.hidden = []
        self.currenplayer.sum()
        self.currenplayer.draw(self.currenplayer, 2)
        
    def __init__(self, play1, play2, starthp): # health, bet
        self.starthp = starthp
        self.p1, self.p2 = player(play1, starthp), player(play2, starthp)
        players = [self.p1, self.p2]
        print(self.p1)
        for i in players:
            self.draw(i, 2)
        self.currenplayer = self.p1
        self.otherplayer = self.p2
        self.gameEmbed = self.build_embed()

class PlayView(discord.ui.View):
    def __init__(self, board):
        super().__init__(timeout=None)
        self.board = board 
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def on_hit_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.draw(self.board.currenplayer, 1)
        self.board.standcount = 0
        await interaction.response.edit_message(embed=self.board.build_embed(), view=self)
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def on_stand_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.currenplayer, self.board.otherplayer = self.board.otherplayer, self.board.currenplayer
        self.board.turn += 1
        self.board.standcount += 1
        if self.board.standcount >=2:
            #resolve round
            pass
        await interaction.response.edit_message(embed=self.board.build_embed(), view=self)
    @discord.ui.button(label="Arcana", style=discord.ButtonStyle.blurple)
    async def on_arcana_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ArcanaView(self.board.currenplayer.tarot)
        await interaction.response.send_message(embed=None, view=view, ephemeral=True)
    @discord.ui.button(label="Debug", style=discord.ButtonStyle.blurple)
    async def on_debug_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.currenplayer.tarot.append(["Test Arcana","A powerful spell.",3])
        self.board.currenplayer.tarot.append(["Test Arcana2","A weak spell.",1])
        await interaction.response.send_message(content="spawning test arcana",ephemeral=True)

class ArcanaView(discord.ui.View):  
    def build_dropdown(self, optionsinp: list[list[str, str,int]]):
        dropdown = discord.ui.Select(
            placeholder="Choose an option...",
            options=[
                discord.SelectOption(label=f"{label} [x{tarotcount}]", description=desc)
                for label, desc, tarotcount in optionsinp
            ],
        )
        return dropdown
    def listcomp(self, inv: list):
        self.templist = []
        self.templist2 = []
        for i in range (len(inv)):
            if inv[i][0] in self.templist2:
                self.templist[self.templist2.index(inv[i][0])][2] += 1
            else:   
                self.templist.append(inv[i])
                self.templist2.append(inv[i][0])
        inv = self.templist
    def __init__(self, tarotinv):
        super().__init__(timeout=None)
        dropdown = self.build_dropdown(tarotinv)
        dropdown.callback = self.select_callback
        self.add_item(dropdown)
        
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Invoking {select.values[0]}.")
    

class AcceptView(discord.ui.View):
    def __init__(self, play1, play2):
        super().__init__(timeout=None)
        self.player1, self.player2 = play1, play2
        print(self.player1)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.blurple)
    async def on_accept_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        board = game(self.player1, self.player2, 7)
        playbuttons = PlayView(board)
        await interaction.response.edit_message(embed=board.gameEmbed, view=playbuttons)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def on_deny_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=None, embed=discord.Embed(
            title="Bluff Challenge",
            description=str(f"Challenge Denied"),
            color=0x363636
        ), view=None)

      
@bot.group(invoke_without_command=True)
async def bluff(ctx):
    await ctx.send('hello')


@bluff.command()
async def duel(ctx, target: discord.Member):
    author = ctx.author
    embed = discord.Embed(
    title="Bluff Challenge",
    description=f"{author.mention} has challenged {target.mention}!",
    color=COLOR
)
    embed.set_footer(text=f"{author} vs {target}")
    accept = AcceptView(author,target)
    await ctx.send(embed=embed, view=accept) 

bot.run(TOKEN)