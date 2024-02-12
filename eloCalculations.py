START_ELO = 1000

eloChangeFactor = 187 # how many half-points you gain per win
eloDeviation = 600 # scales how much the difference in elo increases/decreases how many points you get

playerEloDatabase = {} # temporary until we use mongodb

def createPlayer(name, elo=START_ELO): # adds name to database
    global playerEloDatabase
    playerEloDatabase.update({name:elo})

def simMatch(name1, name2, result: float) -> None: # updates elo database. "result" =1 if name1 wins, =0 if name2 wins, =0.5 if draw
    elo1, elo2 = map(lambda x: playerEloDatabase[x], [name1, name2]) # todo this is also redundant
    chanceOfWinning1 = 1/(1+10**((elo2-elo1)/eloDeviation)) # todo this could be put directly in the elo change statement
    eloChange = eloChangeFactor*(result-chanceOfWinning1)
    playerEloDatabase[name1] = elo1 + eloChange
    playerEloDatabase[name2] = elo2 - eloChange

def oddsOfWinning(name1: str, name2: str) -> float:
    """Calculate the probability name1 beats name2 based on their elos.

    Args:
        name1 (str): The name of the first player
        name2 (str): The name of the second player

    Returns:
        float: odds that name1 wins from 0 to 1
    """
    
    return 1/(1+10**((playerEloDatabase[name2]-playerEloDatabase[name1])/eloDeviation))

def returnLeaderboard() -> list: # given no input, returns [(player, elo), ..] sorted descending by rank
    players = list(playerEloDatabase.keys())
    elos = list(playerEloDatabase.values())
    orderedElos = elos.copy()
    orderedElos.sort()
    orderedElos.reverse()
    leaderboard = []
    for elo in orderedElos:
        loc = elos.index(elo)
        player = players[loc]
        elos[loc] = 0 # cant be found again if its 0
        leaderboard.append((player, elo))
    return leaderboard
