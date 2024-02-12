START_ELO = 1000

eloChangeFactor = 90 # how many half-points you gain per win
eloDeviation = 600 # scales how much the difference in elo increases/decreases how many points you get

# result should be a 0 or a 1. 0 = loss; 1 = win.
def simPuzzle(playerElo, puzzleElo, result) -> int:
    return playerElo + eloChangeFactor*(result-(1/(1+10**((puzzleElo-playerElo)/eloDeviation))))
