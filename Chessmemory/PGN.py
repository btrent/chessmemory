from notation import Node, Notation
from board import Board
from square_utils import *
import utils

class Game:
    # a game contains the following information:
    # - a set of key/value pairs in PGN compatible format
    # - a notation list containing all the moves, variations and commentary
    def __init__(self):
        self.keys = {}
        self.notation_string = ""
        self.notation = Notation()
        self.index = 0
        
        mandatory_keys = ['Event', 'White', 'Black', 'WhiteElo', 'BlackElo', 'Result']
        for key in mandatory_keys:
            self.keys[key] = ""


def parse(filename):
    """PGN game iterator that that yields every game individually."""
    pgnfile = open(filename,'r',1)
    
    game = Game()
    moves = []
    game_index = 0
    for line in pgnfile:
        line = line.strip()
        if len(line) > 0:
            if line[0] == '[':
                if moves: # Return a full game
                    game.index = game_index
                    game.notation_string = '\n'.join(moves)
                    yield game
                    
                    game = Game()
                    moves = []
                    game_index += 1
                # Extract PGN header key and value
                key = line.split()[0][1:]
                value = line.split('"')[1]
                game.keys[key] = value
            elif line[0] != '%':
                moves.append(line)
    if moves: # The last game
        game.index = game_index
        game.notation_string = '\n'.join(moves)
        yield game


def parse_string(string, position=None, parent=None, return_position=False):
    """ Recursively parse a PGN compatible notation string
        string: The string to parse
        position: Starting position
        parent: Parent node (for variations)
        return_position: Whether to return the final position instead of nodes
        Returns an array of nodes or the final position """

    nodes = []
    result_strings = ['1-0', '0-1', '1/2-1/2', '*']
    
    board = Board(position=position)
    
    # create the initial node
    node = Node()
    node.position = board.get_position()
    node.parent = parent
    last_node = node
    nodes.append(node)
    
    i = 0; first_illegal = 0
    while i < len(string):
        if string[i] in ' ' '\n' '\t':
            i += 1
            continue
        
        # Get the next token
        token = string[i:].split()[0]
        
        # Variation
        if token[0] == '(' and not return_position:
            # find the matching bracket
            b, j = 1, i+1
            in_comment = False    # we have to ignore brackets inside of comments
            
            for char in string[j:]:
                j += 1
                if in_comment:
                    if char == "}":
                        in_comment = False
                    continue
                if char == '{':
                    in_comment = True
                    continue
                if char == '(':
                    b+=1
                elif char == ')':
                    b-=1
                if b == 0:
                    break
                    
            variation = string[i+1:j-1]
            i = j + 1
            
            # now recursively parse this string and add it as a variation to the node
            last_node.variations.append(parse_string(variation, last_node.previous.position, node))
        
        # Comment
        elif token[0] == '{' and not return_position:
            j = i + string[i:].find('}')
            comment = string[i+1:j]
            comment = comment.replace('\n', ' ')
            last_node.comment = comment
            i = j + 1
            
        else:
            i += len(token)+1
            
            # strip move number
            if token.find('.') >= 0:
                token = token[token.rfind('.')+1:]
                
            if len(token) < 2:
                continue
            
            # Create a new node    
            node = Node()
            node.move = token
            
            if node.move in result_strings:
                break
            #elif node.move == "O-O-O" or node.move == "0-0-0":
            elif "0-0-0" in node.move or "O-O-O" in node.move:
                board.castle_queenside()
                if board.side_to_move == "black": x = 56
                else: x = 0
                move = {}
                move["square"] = 4 + x
                move["target"] = 2 + x
                node.movelist.append(move)
                move = {}
                move["square"] = 0 + x
                move["target"] = 3 + x
                node.movelist.append(move)
            #elif node.move == "O-O" or node.move == "0-0":
            elif "0-0" in node.move or "O-O" in node.move:
                board.castle_kingside()
                if board.side_to_move == "black": x = 56    
                else: x = 0
                move = {}
                move["square"] = 4 + x
                move["target"] = 6 + x
                node.movelist.append(move)
                move = {}
                move["square"] = 7 + x
                move["target"] = 5 + x
                node.movelist.append(move)
            else:
                m = parse_move(node.move)
                
                if not m:
                    # treat illegal moves as annotations
                    last_node.annotations.append(utils.nag_replace(node.move))
                    continue
                
                target = sq(m["file"]+m["rank"])
                (ax, ay) = alg_to_coord(m["file-ambi"], m["rank-ambi"])
                
                square = None
                square = board.find_move(m["piece"], target, m["capture"], ax, ay)
                if square == None:
                    last_node.comment += "PGN parsing error at %s.\nRemaining moves:\n%s" % (node.move, string[i:])
                    break

                move = {}
                move["square"] = square
                move["target"] = target
                node.movelist.append(move)
                
                board.add_move(square, target, m["piece"], m["capture"], m["promotion"])
            # END IF
            
            board.swap_color()
            node.position = board.get_position()
            
            # Link our shiny new node
            if last_node:
                node.previous = last_node
                last_node.next = node
            nodes.append(node)
            last_node = node
        # END IF
    # END WHILE
    
    if return_position:
        return last_node.position
    else:
        return nodes        


def parse_move(move):
    """ Parse a move in short or long algebraic notation and return a useful data structure. """
    
    ranks = ("1", "2", "3", "4", "5", "6", "7" ,"8")
    files = ("a", "b", "c", "d", "e", "f", "g", "h")
    pieces = ("K", "Q", "R", "B", "N")
    expect = ("piece", "rank", "file")
    
    c_rank = ""
    c_file = ""
    c_promotion = ""
    c_rank_ambi = ""
    c_file_ambi = ""
    c_piece = "P"
    capture = False
    
    # We go from last to first
    for c in move[::-1]:
        if c in ranks:
            if "rank" in expect:
                if c_rank:
                    c_rank_ambi = c
                    expect = ("piece", "finish", "file")
                else:
                    c_rank = c
                    expect = ("file")
            else:
                return None
        elif c in files:
            if "file" in expect:
                if c_file:
                    c_file_ambi = c
                    expect = ("piece", "finish")
                else:
                    c_file = c
                    expect = ("piece", "finish", "rank", "file")
            else:
                return None
        elif c == "x":
            capture = True
        elif c in pieces:
            if "piece" in expect:
                c_piece = c
                expect = ("finish", "promotion")
            else:
                return None
        elif c == "=":
            # Last piece char was a promotion
            if "promotion" in expect:
                c_promotion = c_piece
                c_piece = "P"
                expect = ("rank")
            else:
                return None
    # END FOR
    
    # ignore if not a legal move
    if not "finish" in expect or not c_rank:
        return None
            
    data = {}
    data["piece"] = c_piece
    data["rank"] = c_rank
    data["file"] = c_file
    data["rank-ambi"] = c_rank_ambi
    data["file-ambi"] = c_file_ambi
    data["promotion"] = c_promotion
    data["capture"] = capture
    
    return data
