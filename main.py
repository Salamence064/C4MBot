# I hate Python (C++ >>>)
# yor mother (real)
# what shows u currently watching? me: solo leveling

import discord
import asyncio
import sqlite3

from dotenv import dotenv_values
from discord.ext import commands
from random import randint

from bitboards import checkwin, makemoves, generateMasks

diffAdjectives = ['Newbie', 'Beginner', 'Rookie', 'Novice', 'Intermediate', 'Proficient', 
                  'Advanced', 'Expert', 'Champion', 'Impossible', 'Nod Puzzle']
activeGamePlayers = [] # [(player,channel),(player,channel)]


# returns board (2d list) after sequence of moves (str like '432')
def getBoard(moves: str, boardSize="7x6"):
    try:
        index = boardSize.index('x')
        width = int(boardSize[:index])
        height = int(boardSize[index+1:])

    except: return "Invalid format. Provide the board size as <width>x<height>"

    if (width > 9 or height > 9): return "Board size is too large. The width and height must be between 2-9"
    if (width < 2 or height < 2): return "Board size is too small. The width and height must be between 2-9"

    uniqueMoves = set(moves)
    '''
    for move in uniqueMoves:
        if moves.count(move) > height:
            return f"Invalid input. Too many moves in column {move}"
        
        iMove = int(move)
        if iMove > width or iMove < 1:
            return f"Invalid input. Move string contains invalid column '{iMove}'"
    '''
    board = [[":white_large_square:"]*width for i in range(height)]
    bottomCell = [height-1 for cols in range(width)]
    turn = True

    for move in moves:
        # update the board
        iMove = int(move) - 1
        board[bottomCell[iMove]][iMove] = ":blue_circle:" if turn else ":red_circle:"

        # update for next iteration
        bottomCell[iMove] -= 1
        turn = not turn

    return board


# return discord-formatted message
def getBoardMessage(board, p1, p2, turn):
    p = p1 if turn else p2
    message = p.mention + " It's your turn to play!\n"

    if board != 0:
        message += ":black_large_square:"
        numRows, numColumns = len(board), len(board[0])
        message += " " + " ".join([env[str(num)] for num in range(numColumns)]) + "\n"

        for rowIndex, row in enumerate(board):
            rowNum = str(numRows - rowIndex - 1)
            message += env[rowNum] + " " + " ".join(row) + "\n"

    p1, p2 = "Player 1: " + p1.global_name, "Player 2: " + p2.global_name
    if turn: p1 += " ←"
    else: p2 += " ←"

    message += f"{p1}\n{p2}"
    return message

# Note: player should be either 1 or 2
def getPuzzleEmbed(board: list[list[str]], elo: int, difficulty: int, author: str, player: int, title: str):
    message = f"## Difficulty: {diffAdjectives[difficulty]}\nElo: {elo}\n\n:red_square:"
    rows, cols = len(board), len(board[0])
    message += " ".join([env[str(num)] for num in range(cols)]) + "\n"
    
    for r in range(rows): message += env[str(rows - r - 1)] + " ".join(board[r]) + "\n"

    message += f"\n###### By {author}"

    embed=(discord.Embed(title=title,  color=0xE10101)
                .add_field(name="-help", value="Get information on a command.", inline=False)
                .add_field(name="-flip", value="Flip a coin.", inline=False)
                .set_footer(text="For more information on each command use -help [command]"))

    return embed

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


# * ====================
# * Utility Commands
# * ====================

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
        # determine whether they specified board size or not
        if "x" in arguments: boardSize, moves = arguments.split()
        else: boardSize, moves = "7x6", arguments

        moves = [int(move) for move in moves]
        
    except:
        await ctx.send("Invalid input. Syntax: '-display <board size> <move notation>'")

    await ctx.send(boardSize)
    await ctx.send(moves)


# * ===================
# * Puzzle Commands
# * ===================
    
@bot.command()
async def createpuzzle(ctx, *arguments):
    author = ctx.author.display_name

    # todo go through and add title related stuff

    # todo will later streamline this so the bot prompts for these things and determines the elo and difficulty itself (if possible?)
    # todo if not possible, we can have it manually entered and it can be overridden by us
    # todo for now this is just for testing
    # todo will also allow for the creation of multi-move puzzles

    '''
    Difficulty Legend:
    0 - Newbie
    1 - Beginner
    2 - Rookie
    3 - Novice
    4 - Intermediate
    5 - Proficient
    6 - Advanced
    7 - Expert
    8 - Champion
    9 - Impossible
    10 - Nod Puzzle
    '''

    line = ""
    difficulty = -1
    elo = -1
    solution = -1 # always go 7!!!

    try:
        for arg in arguments:

            if (arg.startswith("line:")):
                line = arg[5:]
                
            elif (arg.startswith("difficulty:")):
                difficulty = int(arg[11:])

            elif (arg.startswith("elo:")):
                elo = int(arg[4:])

            elif (arg.startswith("solution:")):
                solution = int(arg[9:])

            else:
                raise Exception

    except:
        await ctx.send(f"Invalid argument. Unrecgonized token: '{arg}'")
        return
    
    # add the puzzle to the db
    con = sqlite3.connect('connect4.db')
    cur = con.cursor()

    values = [line, elo, difficulty, solution, '7x6', author]
    cur.execute("INSERT INTO Puzzles VALUES (?,?,?,?,?,?)", values)

    con.commit()
    con.close()

    await ctx.send("Puzzle successfully added.")

@bot.command()
async def playpuzzle(ctx, arg):
    # todo currently also set up for debugging stuff
    # ! for debugging a line will be passed in and it will simply display that puzzle to the screen
    
    # query the puzzle from the db
    con = sqlite3.connect('connect4.db')
    cur = con.cursor()

    try: cur.execute('SELECT * FROM Puzzles WHERE Line=?', (arg,))
    except: await ctx.send(f"Line '{arg}' is not an existing puzzle."); return

    values = cur.fetchone() # retrieve the values from the query
    con.close()

    board = getBoard(arg, values[4])
    solution = values[3]

    await ctx.send(embed=getPuzzleEmbed(board, values[1], values[2], values[5], (len(arg)&1) + 1))


# * =====================
# * Gameplay Commands
# * =====================

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
    blindfolded, preset_moves = False, 0

    # ensure preset_moves flag is located after boardsize flag
    for flagnum, flag in enumerate(flags):
        if flag[0] in map(str, [i for i in range(1, width+1)]) and flag[1] != 'x':
            flags = flags[:flagnum] + flags[flagnum+1:] + (flags[flagnum],)
            break

    try:
        for flag in flags:
            currentflag = flag
            if flag[1] == "x":
                width, height = int(flag[0]), int(flag[2:])
                if (width > 9 or height > 9) or (width < 2 or height < 2): raise Exception

            elif flag.startswith("wincondition=") or flag.startswith("wc="):
                wincondition = int(flag[flag.index("=")+1:])
                if (wincondition > width or wincondition > height) or wincondition < 2:
                    raise Exception
            
            elif flag == "blindfolded" or flag == "bf":
                blindfolded = True

            # this condition must be last because it assumes int. here you set starting position ('436')
            else:
                characters = {char for char in flag}
                legalcharacters = {str(i) for i in range(1, width+1)}
                if not characters - legalcharacters: # i.e make sure only valid characters are used
                    preset_moves = flag
                    for char in characters:
                        if preset_moves.count(char) > height:
                            raise Exception
                

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

            if (msg.author, msg.channel) in activeGamePlayers and 0:
                await ctx.send(player2.mention + " is already playing a game in this channel")
                continue

            #await ctx.send(player2.mention + " has joined the game, now starting")
            activeGamePlayers.append((msg.author, msg.channel))

            # board initializing

            board = [[":white_large_square:"]*width for i in range(height)]
            bottomCell = [height-1 for cols in range(width)]
            moves = ""

            if blindfolded:
                board = 0
            if preset_moves:
                preset_moves
                moves = str(preset_moves)
                turn = bool(~len(moves)%2)
                boardSize = str(width) + "x" + str(height)
                board = getBoard(moves, boardSize)
                
                for move in moves:
                    bottomCell[int(move)-1] -= 1
                
            await ctx.send(getBoardMessage(board, player1, player2, turn))
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
            await ctx.send(getBoardMessage(board, player1, player2, turn))
            return await ctx.send(msg.author.mention + " won the game!")
            
        turn = not turn
        await ctx.send(getBoardMessage(board, player1, player2, turn))




# run the bot
bot.run(env["TOKEN"])
