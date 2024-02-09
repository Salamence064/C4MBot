import time


# generates the masks used to prevent bitshift overflow
def generateMasks(width, height, wincondition):
    width, height = 7, 6
    wincondition = 4

    rowmask = "0"*(wincondition-1) + "1"*(width-wincondition+1)
    rowsmask = "".join([rowmask*height])
    horizontalmask = int(rowsmask, 2)

    columnsmask = "".join(["0"*width*(wincondition-1)] + ["1"*width*(height-wincondition+1)])
    verticalmask = int(columnsmask, 2)

    diagonalmask = "1"*(width-wincondition+1) + "0"*(wincondition-1) # used for only downdiagonalmask. updiagonalmask is same as horizontalmask
    diagonalmasks = "".join([diagonalmask*height])
    downdiagonalmask = int(diagonalmasks, 2)

    masks = (horizontalmask, verticalmask, downdiagonalmask)
    return masks

# returns bitboard after 1 move
def makemove(move, bitboard, width, height, layer): # 
    layerHeight = layer[move-1]
    moveBin = (1 << move-1) << width*layerHeight
    bitboard |= moveBin
    return bitboard

# returns 2 bitboards of position after moves
def makemoves(moves: str, width, height):
    bitboard1, bitboard2 = 0, 0
    layer = [0 for i in range(width)]
    while moves:
        move, moves = int(moves[0]), moves[1:]
        bitboard1 = makemove(move, bitboard1, width, height, layer)
        layer[move-1] += 1
        if moves:
            move, moves = int(moves[0]), moves[1:]
            bitboard2 = makemove(move, bitboard2, width, height, layer)
            layer[move-1] += 1
        else:
            break
    return bitboard1, bitboard2

# prints binary version of a number
def binprint(bitboard):
    print(bitboard, format(bitboard, "b"))

# prints display board in terminal of bitboard
def printboard(bitboard, width, height):
    for row in range(height-1, -1, -1):
        for col in range(width):
            if bitboard & (1 << (width*row+col)):
                print("1", end = " ")
            else:
                print("0", end = " ")
        print()

# returns True or False if theres a win on that bitboard
def checkwin(bitboard, width, height, wincondition, masks):
    horizontalmask, verticalmask, downdiagonalmask = masks[0], masks[1], masks[2]
    wincondition -= 1

    horizontalboard = bitboard
    for i in range(wincondition):
        horizontalboard &= (horizontalboard >> 1)
    horizontalboard &= horizontalmask
    if horizontalboard:
        return True
    
    verticalboard = bitboard
    for i in range(wincondition):
        verticalboard &= (verticalboard >> width)
    verticalboard &= verticalmask
    if verticalboard:
        return True
    
    updiagonalboard = bitboard
    for i in range(wincondition):
        updiagonalboard &= (updiagonalboard >> (width+1))
    updiagonalboard &= horizontalmask
    if updiagonalboard:
        return True

    downdiagonalboard = bitboard
    for i in range(wincondition):
        downdiagonalboard &= (downdiagonalboard >> (width-1))
    downdiagonalboard &= downdiagonalmask
    if downdiagonalboard:
        return True

    return False




# THIS IS THE BIG BEANS
# GREAT GOOGLY GUACAMOLE

def solver(state):
    if state == "big chungus":
        return 10
    return -10