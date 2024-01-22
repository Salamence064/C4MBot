# I hate Python (C++ >>>)

from dotenv import dotenv_values
import discord
import asyncio
from discord.ext import commands
from random import randint


# used to avoid the bot locking in on one random number
def randomNumber(): return randint(0, 1)


# convert a double list to a string
def printBoard(board, offset):
    message = ""
    
    for i in range(len(board)):
        message += board[i]
        if (i%offset == 7): message += "\n"
        else: message += " "

    return message


# import token from .env file
env = dotenv_values(".env") # will give us a dictionary with all values from .env


# initialize the intents
intents = discord.Intents.default()
intents.message_content = True


# setup bot
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

@bot.command()
async def c4(ctx, arg = "7x6"):
    try:
        index = arg.index('x')

        width = int(arg[:index])
        height = int(arg[index+1:])

    except:
        await ctx.send("Invalid format. Provide the board size as <width>x<height>")
        return

    if (width > 9 or height > 9):
        await ctx.send("Board size is too large. The width and height must be between 2-9.")
        return
    
    if (width < 2 or height < 2):
        await ctx.send("Board size is too small. The width and height must be between 2-9.")
        return
    
    # track if this instance of the game is still running
    gameRunning = True
    turn = True # True = P1, False = P2

    # setup numbers at the top
    message = ":black_large_square: "
    for i in range(width):  message += env[str(i)] + " "
    message += "\n"

    # empty board config
    for i in range(height-1, -1, -1): message += env[str(i)] + " " + ":white_large_square: " * width + "\n"
    await ctx.send(message)

    # gameboard used for display
    board = message.split()

    # setup for quicker move making
    c = width + 1
    bottomCell = [height*c + i for i in range(0, c)]
    
    while gameRunning:
        try: msg = await bot.wait_for('message', check=None, timeout=300)
        except asyncio.TimeoutError: return await ctx.send("Game timed out.")

        # ensure the input is a valid column
        try:
            mv = int(msg.content)

            if mv < 1 or mv > width:
                await ctx.send("Invalid move.")
                continue

            if bottomCell[mv] < c:
                await ctx.send("Full column.")
                continue

            board[bottomCell[mv]] = ":blue_circle:" if turn else ":red_circle:"
            bottomCell[mv] -= c
            turn = not turn
            await ctx.send(printBoard(board, width+1))

        except:
            gameRunning = False
            await ctx.send("Game complete.")


# run the bot
bot.run(env["TOKEN"])
