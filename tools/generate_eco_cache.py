#!/usr/bin/python

import Chessmemory.PGN as PGN
def parse(filename):
    sourcefile = open(filename,'r',1)
    positionfile = open("eco.positions",'w')
    
    all_moves = ""
    
    for line in sourcefile:
        if len(line) > 1 and line[0] != '#':
            description = line.split('  ')[0].strip()
            try:
                moves = line.split('  ')[1].strip()
            except IndexError:
                moves = ""

            try:
                eco = description.split()[0]
            except IndexError:
                pass
                
            try:
                name = description.split('"')[1]
            except IndexError:
                pass

            all_moves += " " + moves
            
            if len(moves) > 0 and moves[-1] == '*':
                print eco
                fen = PGN.parse_string(all_moves, return_position=True).get_FEN()
                positionfile.write(fen+'  '+eco+'  '+name+'\n')
                all_moves = ""
        # END IF
    # END FOR
    
if __name__ == "__main__":
    parse("eco.source")
    