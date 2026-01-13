import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

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
    currenplayer = None  
    goal = 21
    gameEmbed = discord.Embed
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
            description=str(self.deck),
            color=discord.Color.blurple()
        )
        embed.add_field(name=self.p1.player, value=self.p1.hand, inline=True)
        embed.add_field(name=self.p2.player, value=self.p2.hand, inline=True)
        embed.add_field(name="\u000b", value="\u000b", inline=False)
        embed.add_field(name="Hand", value=self.p1.hidden, inline=True)
        embed.add_field(name="Hand", value=self.p2.hidden, inline=True)
        embed.set_footer(text=f"{self.p1.player} vs {self.p2.player}")
        return embed
    def __init__(self, play1, play2, starthp): # health, bet
        self.starthp = starthp
        self.p1, self.p2 = player(play1, starthp), player(play2, starthp)
        players = [self.p1, self.p2]
        print(self.p1)
        for i in players:
            self.draw(i, 2)
        self.gameEmbed = self.build_embed()
        self.currenplayer = self.p1
        self.otherplayer = self.p2


#instancex = game("me", "you")
#playerx = player(instancex.p1)
#playery = player(instancex.p2)
#playerx.health = instancex.p1health

class PlayView(discord.ui.View):
    def __init__(self, board):
        super().__init__(timeout=None)
        self.board = board 
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def on_accept_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.draw(self.board.currenplayer, 1)
        await interaction.response.edit_message(embed=self.board.build_embed(), view=self)
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def on_deny_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.currenplayer, self.board.otherplayer = self.board.otherplayer, self.board.currenplayer
        await interaction.response.edit_message(embed=self.board.build_embed(), view=self)

class AcceptView(discord.ui.View):
    # This button will have a red style and the label "Click Me!"

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
        """Callback fself.player1,self.player2unction for the button click."""
        # Acknowledge the interaction and edit the mesboard.gameEmbed        await interaction.response.edit_message(content="Button clicked!", embed=None, view=None)

      
@bot.group(invoke_without_command=True)
async def bluff(ctx):
    await ctx.send('hello')


@bluff.command()
async def duel(ctx, target: discord.Member):
    author = ctx.author
    embed = discord.Embed(
    title="Bluff Challenge",
    description=f"{author.mention} has challenged {target.mention}!",
    color=discord.Color.blurple()
)
    embed.set_footer(text=f"{author} vs {target}")
    accept = AcceptView(author,target)
    await ctx.send(embed=embed, view=accept) 

bot.run(TOKEN)