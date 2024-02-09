# I hate Python (C++ >>>)
# yor mother (real)

from dotenv import dotenv_values
import discord
import asyncio
from discord.ext import commands
from random import randint
from bitboards import checkwin, makemoves, generateMasks

activeGamePlayers = [] # [(player,channel),(player,channel)]

# returns board (2d list) after sequence of moves (str like '432')
def getBoard(moves: str, boardSize="7x6"):
    moveList = []
    moveList.extend(moves)
    try:
        index = boardSize.index('x')
        width = int(boardSize[:index])
        height = int(boardSize[index+1:])

    except: return "Invalid format. Provide the board size as <width>x<height>"
    if (width > 9 or height > 9): return "Board size is too large. The width and height must be between 2-9"
    if (width < 2 or height < 2): return "Board size is too small. The width and height must be between 2-9"

    uniqueMoves = set(moveList)
    for move in uniqueMoves:
        if moveList.count(move) >= height:
            return f"Invalid input. Too many moves in column {move}"

    board = [[":white_large_square:"]*width for i in range(height)]
    bottomCell = [height-1 for cols in range(width)]
    
# return discord-formatted message
def getBoardMessage(board, p1_ping, p2_ping, turn):
    message = ""
    if board != 0:
        message += ":white_large_square:"
        numRows, numColumns = len(board), len(board[0])
        message += " ".join([env[str(num)] for num in range(numColumns)])
        message += "\n"
        for rowIndex, row in enumerate(board):
            rowNum = str(numRows - rowIndex - 1)
            text = env[rowNum] + " ".join(row) + "\n"
            message += text
    p1_ping, p2_ping = "Player 1: " + p1_ping, "Player 2: " + p2_ping
    if turn: p1_ping += " ←"
    else: p2_ping += " ←"
    message += f"{p1_ping}\n{p2_ping}"
    return message

def isWinCondition(moves, turn, width, height, wincondition):
    masks = generateMasks(width, height, wincondition)
    bitboard1, bitboard2 = makemoves(moves, width, height)
    if turn: bitboard = bitboard1
    else: bitboard = bitboard2

    result = checkwin(bitboard, width, height, wincondition, masks)
    return result

# import token from .env file
env = dotenv_values(".env")

# initialize intents
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
async def flip(ctx): await ctx.send("**heads**" if randint(0, 1) == 1 else "**tails**")

@bot.command()
async def display(ctx, *arguments):
    arguments = " ".join(arguments)
    try:
        if "x" in arguments: # determine whether they specified board size or not
            boardSize, moves = arguments.split()
        else:
            boardSize, moves = "7x6", arguments
        moves = [int(move) for move in moves]
    except:
        await ctx.send("Invalid input. Syntax: '-display <board size> <move notation>'")
    await ctx.send(boardSize)
    await ctx.send(moves)

@bot.command()
async def series(ctx):
    playera = ctx.author
    await ctx.send(playera.mention + " has started a series. Type '-joinseries' to join")
    try:
        msg = await bot.wait_for('message', check=lambda msg: msg.content == "-joinseries" and msg.author != playera, timeout=300)
    except asyncio.TimeoutError:
        await ctx.send("The series timed out")
    playerb = msg.author
    await ctx.send(playerb.mention + " has joined the series, now starting")


@bot.command()
async def start(ctx, *flags):
    global activeGamePlayers

    # prevent duplicate games
    if (ctx.author, ctx.channel) in activeGamePlayers:
        await ctx.send(ctx.author.mention + " is already playing a game in this channel!")
        gameRunning = False
    else:
        activeGamePlayers.append((ctx.author, ctx.channel))
        gameRunning = True
        turn = True # True = P1, False = P2

    # flags
    width, height = 7, 6
    wincondition = 4
    blindfolded = False
    try:
        for flag in flags:
            currentflag = flag
            if flag[1] == "x":
                width, height = int(flag[0]), int(flag[2:])
                if (width > 9 or height > 9) or (width < 2 or height < 2): raise Exception
            
            #if flag.startswith("board"): # set custom starting position

            elif flag.startswith("wincondition=") or flag.startswith("wc="):
                wincondition = int(flag[flag.index("=")+1:])
                if (wincondition > width or wincondition > height) or wincondition < 2:
                    raise Exception
            
            elif flag == "blindfolded" or flag == "bf":
                blindfolded = True
            
            else:
                raise Exception



    except:
        await ctx.send(f"Invalid flag format. Issue here → `{currentflag}`")
        activeGamePlayers.remove((ctx.author, ctx.channel))
        gameRunning = False
        

    if gameRunning:
        player1 = ctx.author
        await ctx.send(player1.mention + " has started a game. Type '-join' to join")

        while True:
            # await a second player joining
            try:
                msg = await bot.wait_for('message', check=None, timeout=300)
                player2 = msg.author
            except asyncio.TimeoutError:
                await ctx.send("The game timed out")
                activeGamePlayers.remove((ctx.author, ctx.channel))
                gameRunning = False
                break
            if msg.channel != ctx.channel: continue
            if msg.content == "-quit":
                gameRunning = False
                activeGamePlayers.remove((player1, ctx.channel))
                await ctx.send(player2.mention + " quit the game")
                break
            if msg.content != "-join": # ignore any messages that arent joining
                continue
            if (msg.author, msg.channel) in activeGamePlayers:
                await ctx.send(player2.mention + " is already playing a game")
                continue

            await ctx.send(player2.mention + " has joined the game, now starting")
            activeGamePlayers.append((msg.author, msg.channel))

            # board initializing
            board = [[":white_large_square:"]*width for i in range(height)]
            bottomCell = [height-1 for cols in range(width)]
            moves = ""
            if blindfolded:
                board = 0
            await ctx.send(getBoardMessage(board, player1.mention, player2.mention, turn))
            break
    
    while gameRunning:
        # actual game logic
        try: msg = await bot.wait_for('message', check=None, timeout=300)
        except asyncio.TimeoutError:
            activeGamePlayers.remove((player1, ctx.channel))
            activeGamePlayers.remove((player2, ctx.channel))
            return await ctx.send("Game timed out.")
        if msg.channel != ctx.channel:
            continue

        if msg.content == "-quit":
            gameRunning = False
            await ctx.send(msg.author.mention + " quit the game")
            activeGamePlayers.remove((player1, ctx.channel))
            activeGamePlayers.remove((player2, ctx.channel))

        # ensure the input is a valid column
        try:
            mv = int(msg.content)
            if mv < 1 or mv > width:
                await ctx.send(f"Move must be within range 1-{width}")
                continue
            mv -= 1 # for indexing purposes
            if bottomCell[mv] < 0:
                await ctx.send("This column is full")
                continue
        except ValueError:
            continue
        except:
            gameRunning = False
            await ctx.send("error")
            activeGamePlayers.remove((player1, ctx.channel))
            activeGamePlayers.remove((player2, ctx.channel))

        height = bottomCell[mv]
        if not blindfolded:
            board[height][mv] = ":blue_circle:" if turn else ":red_circle:"
        bottomCell[mv] -= 1
        moves += str(mv+1)

        if isWinCondition(moves, turn, width, height, wincondition):
            gameRunning = False
            activeGamePlayers.remove((player1, ctx.channel))
            activeGamePlayers.remove((player2, ctx.channel))
            await ctx.send(getBoardMessage(board, player1.mention, player2.mention, turn))
            return await ctx.send(msg.author.mention + " won the game!")
            
        turn = not turn
        await ctx.send(getBoardMessage(board, player1.mention, player2.mention, turn))




# run the bot
bot.run(env["TOKEN"])
