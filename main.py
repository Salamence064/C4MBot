from dotenv import dotenv_values
import discord
from discord.ext import commands
from random import randint


def randomNumber(): return randint(0, 1)


# import token from .env file
env = dotenv_values(".env") # will give us a dictionary with all values from .env


# initialize the bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)


# commands
@bot.command()
async def help(ctx, arg=""):
    embed=(discord.Embed(title="__List of Commands__",  color=0xE10101)
                        .add_field(name="-help", value="Get information on a command.", inline=False)
                        .add_field(name="-flip", value="Flip a coin.", inline=False)
                        .set_footer(text="For more information on each command use -help [command]"))
    await ctx.send(embed=embed)

@bot.command()
async def flip(ctx): await ctx.send("**heads**" if randomNumber() == 1 else "**tails**")


# run the bot
bot.run(env["TOKEN"])
