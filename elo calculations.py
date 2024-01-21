
START_ELO = 1000

eloChangeFactor = 187 # how many half-points you gain per win
eloDeviation = 600 # scales how much the difference in elo increases/decreases how many points you get


playerEloDatabase = {}

def createPlayer(name, elo=START_ELO): # adds name to database
    global playerEloDatabase
    playerEloDatabase.update({name:elo})

def simMatch(name1, name2, result: float) -> None: # updates elo database. "result" =1 if name1 wins, =0 if name2 wins, =0.5 if draw
    elo1, elo2 = map(lambda x: playerEloDatabase[x], [name1, name2])
    chanceOfWinning1 = 1/(1+10**((elo2-elo1)/eloDeviation))
    chanceOfWinning2 = 1-chanceOfWinning1
    eloChange = eloChangeFactor*(result-chanceOfWinning1)
    playerEloDatabase[name1] = elo1 + eloChange
    playerEloDatabase[name2] = elo2 - eloChange

def oddsOfWinning(name1, name2) -> float: # odds that name1 wins from 0 to 1
    elo1, elo2 = map(lambda x: playerEloDatabase[x], [name1, name2])
    chanceOfWinning1 = 1/(1+10**((elo2-elo1)/eloDeviation))
    return(chanceOfWinning1)

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




    
createPlayer("w")
createPlayer("a")
createPlayer("Miles", 1100)
createPlayer("Radiant")
simMatch("Miles", "Radiant", 1)
simMatch("Miles", "Radiant", 1)

returnLeaderboard()