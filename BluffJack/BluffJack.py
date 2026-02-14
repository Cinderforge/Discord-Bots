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
        self.id = player.id
        self.hand, self.hidden, self.tarot, self.psum, self.hsum= [], [], [], 0, 0
    def sum(self):
        self.psum = sum(self.hand)
        self.hsum = sum(self.hidden)


class game():
    def build_embed(self) -> discord.Embed:
        
        embed = discord.Embed(
            title="Bluff Challenge",
            description=str(f"Bust Limit: {self.goal}"),
            color=COLOR
        )
        embed.add_field(name=f"{self.p1.player}", value=f"HP {self.p1.health}", inline=True)
        embed.add_field(name=f"{self.p2.player}", value=f"HP {self.p2.health}", inline=True)
        embed.add_field(name="\u000b", value="\u000b", inline=False)
        embed.add_field(name="Hand", value=self.p1.hidden, inline=True)
        embed.add_field(name="Hand", value=self.p2.hidden, inline=True)
        embed.set_footer(text=f"Turn {self.turn} | Bet {self.currenbet} | {self.currenplayer.player}'s turn")
        return embed
    
    def beginDraw(self, player):
        for _ in range(2):
            drawn = random.choice(self.deck)
            player.hand.append(drawn)
            player.hidden.append(0)
            self.deck.remove(drawn)
        
    def endround(self):
        print(f"{self.currenplayer.player} other {self.otherplayer.player}")
        print(f"{self.currenplayer.player}'s Score: {self.currenplayer.psum} {self.otherplayer.player}'s Score: {self.otherplayer.psum}")
        winner = None
        if self.currenplayer.psum == self.otherplayer.psum:
            print("Tie!")
        elif (self.currenplayer.psum > self.goal) != (self.otherplayer.psum > self.goal):
            winner = min(self.currenplayer.psum, self.otherplayer.psum)
        elif self.currenplayer.psum > self.goal and self.otherplayer.psum > self.goal:  
            winner = min(self.currenplayer.psum, self.otherplayer.psum)
        else:
            winner = max(self.currenplayer.psum, self.otherplayer.psum)
        if self.currenplayer.psum == winner:
            print(f"{self.currenplayer.player} wins!")
            self.currenplayer.health += self.currenbet
            self.otherplayer.health -= self.currenbet
        elif self.otherplayer.psum == winner:
            print(f"{self.otherplayer.player} wins!")
            self.otherplayer.health += self.currenbet
            self.currenplayer.health -= self.currenbet
        if self.currenplayer.health <= 0:
            print(f"{self.otherplayer.player} has won!")
        elif self.otherplayer.health <= 0:
            print(f"{self.currenplayer.player} has won!")
        self.standcount = 0
        self.currenbet += 1
        self.turn += 1
    def gameover():
        pass
    def fool(self):
        for i in self.currenplayer.hand:
            self.deck.append(i)
        self.currenplayer.hand = []
        self.currenplayer.hidden = []
        self.currenplayer.sum()
        self.currenplayer.draw(self.currenplayer, 2)
        
    def __init__(self, play1, play2, starthp): # health, bet
        self.currenplayer = player  
        self.goal = 21
        self.gameEmbed = discord.Embed
        self.turn = 1
        self.currenbet = 1
        self.standcount = 0
        self.deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.starthp = starthp
        self.p1, self.p2 = player(play1, self.starthp), player(play2, self.starthp)
        players = [self.p1, self.p2]
        print(self.p1)
        for i in players:
            self.beginDraw(i)
        self.currenplayer = self.p1
        self.otherplayer = self.p2
        self.gameEmbed = self.build_embed()

class PlayView(discord.ui.View):
    def __init__(self, board, timeout: int = None):
        super().__init__(timeout=timeout)
        self.board = board 

    async def on_timeout(self):
        self.board.currenplayer.hand.append('X')
        self.board.currenplayer, self.board.otherplayer = (
            self.board.otherplayer,
            self.board.currenplayer,
        )
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.board.currenplayer.id:
            embed = discord.Embed(
                title="Bluff Message",
                description=str(f"It is not your turn!"),
                color=COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False  
        return True  
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def on_hit_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.board.currenplayer.psum > self.board.goal:
            embed = discord.Embed(
                title="Bluff Message",
                description=str("Bro you busted."),
                
                color=COLOR
            )
            embed.set_image(url="https://media.tenor.com/I50TI2DmFXIAAAAM/yuji-stare-yuji-itadori.gif")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if len(self.board.deck) > 0:
                drawn = random.choice(self.board.deck)
                self.board.currenplayer.hand.append(drawn)
                self.board.currenplayer.hidden.append(drawn)
                self.board.deck.remove(drawn)
                self.board.standcount = 0
                await interaction.response.edit_message(embed=self.board.build_embed(), view=self)
            else:
                embed = discord.Embed(
                title="Bluff Message",
                description=str(f"Empty deck!"),
                color=COLOR
            )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            self.board.currenplayer.sum()
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def on_stand_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.currenplayer, self.board.otherplayer = self.board.otherplayer, self.board.currenplayer
        self.board.standcount += 1
        if self.board.standcount >=2:
            self.board.endround()
        await interaction.response.edit_message(embed=self.board.build_embed(), view=self)
    
    @discord.ui.button(label="Arcana", style=discord.ButtonStyle.blurple)
    async def on_arcana_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ArcanaView(self.board.currenplayer.tarot)
        self.board.currenplayer.tarot = view.newlist
        await interaction.response.send_message(embed=None, view=view, ephemeral=True)
    
    @discord.ui.button(label="Hand", style=discord.ButtonStyle.gray)
    async def on_hand_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content=f"Your hand: {self.board.currenplayer.hand}\nHidden: {self.board.currenplayer.hidden}\nTotal: {self.board.currenplayer.psum}",ephemeral=True)
    
    @discord.ui.button(label="Debug", style=discord.ButtonStyle.blurple)
    async def on_debug_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board.currenplayer.tarot.append(["Test Arcana","A powerful spell.",3])
        self.board.currenplayer.tarot.append(["Test Arcana2","A weak spell.",1])
        await interaction.response.send_message(content="spawning test arcana",ephemeral=True)

class ArcanaView(discord.ui.View):  
    def build_dropdown(self, optionsinp: list[list[str, str,int]]):
        optionsinp = self.listcomp(optionsinp)

        dropdown = discord.ui.Select(
            placeholder="Choose an option...",
            options=[
                discord.SelectOption(label=f"{label} [x{tarotcount}]", description=desc)
                for label, desc, tarotcount in optionsinp
            ],
        )
        return dropdown
    def listcomp(self, inv: list):
        self.newlist = []
        self.namelist = []
        for i in range (len(inv)):
            if inv[i][0] in self.namelist:
                self.newlist[self.namelist.index(inv[i][0])][2] += inv[i][2]
            else:   
                self.newlist.append(inv[i])
                self.namelist.append(inv[i][0])
        inv = self.newlist
        return inv
    def __init__(self, tarotinv):
        super().__init__(timeout=None)
        dropdown = self.build_dropdown(tarotinv)
        dropdown.callback = self.select_callback
        self.add_item(dropdown)
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Invoking {select.values[0]}.")
    

class AcceptView(discord.ui.View):
    def __init__(self, play1, play2):
        super().__init__(timeout=30.0)
        self.player1, self.player2 = play1, play2
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.player2.id:
            embed = discord.Embed(
                title="Bluff Message",
                description=str(f"Not you lil bro..."),
                color=COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False  
        return True
    
    async def on_timeout(self):
        if self.message:
            await self.message.edit(content=None, embed=discord.Embed(
                title="Bluff Challenge",
                description=str(f"Challenge Timed Out"),
                color=0x363636
                ), view=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.blurple)
    async def on_accept_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        board = game(self.player1, self.player2, 7)
        playbuttons = PlayView(board)
        await interaction.response.edit_message(embed=board.gameEmbed, view=playbuttons)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def on_deny_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=None, embed=discord.Embed(
            title="Bluff Challenge",
            description=str(f"Challenge Denied"),
            color=0x363636
        ), view=None)
        self.stop()

      
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
    accept.message = await ctx.send(embed=embed, view=accept)

bot.run(TOKEN)