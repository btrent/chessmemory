
square_names =     ["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
                "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
                "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
                "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
                "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
                "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
                "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
                "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"]

# Convert a square name to an index value    
def sq(name):
    for i in range(64):
        if square_names[i] == name: return i
    return -1
    
def square_number(fyle, rank):
    return rank * 8 + fyle
    
def square_file(square):
    return square % 8
    
def square_rank(square):
    return square / 8
    
def square_shift(square, direction):
    res = square
    if "N" in direction:
        res += 8
    if "S" in direction:
        res -= 8
    if "E" in direction:
        res += 1
    if "W" in direction:
        res -= 1
    return res
    
# Returns whether the target square can be reached by a knight hop
def square_knighthop(square, target):
    xDist = abs(square_file(square) - square_file(target))
    yDist = abs(square_rank(square) - square_rank(target))
    return (xDist == 2 or yDist == 2) and xDist+yDist == 3
    
# Return the direction from square to target
def square_direction(square, target):
    xDist = abs(square_file(square) - square_file(target))
    yDist = abs(square_rank(square) - square_rank(target))
    if (xDist > 0 and yDist > 0) and xDist != yDist: return None

    if square_file(target) > square_file(square):
        if square_rank(target) > square_rank(square):
            return "NE"
        elif square_rank(target) < square_rank(square):
            return "SE"
        else:
            return "E"
    elif square_file(target) < square_file(square):
        if square_rank(target) > square_rank(square):
            return "NW"
        elif square_rank(target) < square_rank(square):
            return "SW"
        else:
            return "W"
    else:
        if square_rank(target) > square_rank(square):
            return "N"
        elif square_rank(target) < square_rank(square):
            return "S"
        else:
            return None
            
def square_distance(square, target):
    xDist = abs(square_file(square) - square_file(target))
    yDist = abs(square_rank(square) - square_rank(target))
    return max(xDist, yDist)

# Convert algebraic notation to coordination system
def alg_to_coord(iFile, iRow):
    files = {"a": 0, "b": 1, "c": 2, "d": 3,
             "e": 4, "f": 5, "g": 6, "h": 7}
    if iFile:
        retX = files[iFile]
    else:
        retX = -1
    if iRow:
        retY = int(iRow)-1
    else:
        retY = -1
    return (retX, retY)
    
# Convert coordination system to algebraic notation
def coord_to_alg(x, y):
    files = ("1", "2", "3", "4", "5", "6", "7" ,"8")
    rows = ("a", "b", "c", "d", "e", "f", "g", "h")
    return (files[x], rows[y])
    
def swap_color(color):
    if color == "white": return "black"
    else: return "white"