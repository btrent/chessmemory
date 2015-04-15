# A static representation of a board position.

from pieces import piece_handle_to_letter
from square_utils import *

class Position:
    def __init__(self):
        self.squares = []
        self.fullmove_number = 1
        self.side_to_move = "white"
        self.en_passant_file = None    # the file on which e.p. capture is possible 
        self.en_passant_square = None    # the square on which the last e.p. capture happened
        self.castling_availability = ['K', 'Q', 'k', 'q']
        self.halfmove_clock = 0
        
    def get_FEN(self):
        """Return the FEN string for this position."""
        fen = ""
        empty_count = 0;
        
        # Field 1: Piece placement
        # (Keep in mind that our squares go from bottom to top, opposite to the FEN spec)
        for rank in range(7, -1, -1):
            for line in range(8):
                piece = piece_handle_to_letter(self.squares[rank*8+line], True)
                if piece:
                    if empty_count > 0: 
                        fen += str(empty_count)
                        empty_count = 0
                    fen += piece
                else:
                    empty_count += 1
            # END FOR line
            
            if empty_count > 0:
                fen += str(empty_count)
                empty_count = 0
            if rank > 0: fen += '/'
        # END FOR rank
        
        fen += ' '
        
        # Field 2: Active color
        if self.side_to_move == "white":
            fen += 'w'
        else:
            fen += 'b'
        
        fen += ' '
            
        # Field 3: Castling availability
        if len(self.castling_availability) > 0:
            for x in self.castling_availability:
                fen += x
        else:
            fen += '-'
            
        fen += ' '
        
        # Field 4: En Passant target square
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        if self.en_passant_file:
            fen += files[self.en_passant_file]
            if self.side_to_move == "white":
                fen += '6'
            else:
                fen += '3'
        else:
            fen += '-'
            
        fen += ' '
        
        # Fielf 5/6: Halfmove clock & Fullmove number
        fen += str(self.halfmove_clock) + ' ' + str(self.fullmove_number) 
        
        return fen
        
    def is_legal(self):
        king_square = 0
        
        if self.side_to_move == "white":
            king = "bk"
            check_pieces = ["wp", "wn", "wb", "wr", "wq", "wk"]
        else:
            king = "wk"
            check_pieces = ["bp", "bn", "bb", "br", "bq", "bk"]
    
        # the side to move may not be giving check
        for i in range(64):
            if self.squares[i] == king:
                king_square = i
                break
                
        for i in range(64):
            if self.squares[i] in check_pieces:
                if self.square_can_attack(i, king_square):
                    return False
                
        return True
    
    # Check whether a piece on the given square can attack the target.
    def square_can_attack(self, square, target, type = ""):
        type = type or piece_handle_to_letter(self.squares[square])
        direction = square_direction(square, target)
        distance = square_distance(square, target)
        if type == "P":
            if self.side_to_move == "white":
                if direction in ("NE", "NW") and distance == 1:
                    return True
            else:
                if direction in ("SE", "SW") and distance == 1:
                    return True
        elif type == "N":
            if square_knighthop(square, target): return True
        elif type == "B":
            if direction in ("NE", "NW", "SE", "SW"):
                ts = square
                while 1:
                    ts = self.square_move(ts, target, direction)
                    if not ts or ts == target: break
                if ts == target: return True
        elif type == "R":
            if direction in ("N", "S" , "E", "W"):
                ts = square
                while ts != target:
                    ts = self.square_move(ts, target, direction)
                    if not ts or ts == target: break
                if ts == target: return True
        elif type == "Q":
            if direction:
                ts = square
                while ts != target:
                    ts = self.square_move(ts, target, direction)
                    if not ts or ts == target: break
                if ts == target: return True
        elif type == "K":
            if direction and distance == 1: return True
        
        return False


    # Moves one square into the given direction and returns the resulting square (or None if blocked)
    def square_move(self, square, target, direction):
        res = square
        if "N" in direction:
            res += 8
        if "S" in direction:
            res -= 8
        if "E" in direction:
            res += 1
        if "W" in direction:
            res -= 1
        
        if res < 0 or res > 63: return None
        if res == target: return res
        if self.squares[res]: return None
        return res
        
    def _print(self):
        res = ""
        for i in range(64):
            if i % 8 == 0:
                print res
                res = ""
            sq = self.squares[i]
            if not sq: sq = "__"
            res += sq + " "
        print res