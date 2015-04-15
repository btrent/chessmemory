import cairo
from utils import locate_data_dir

d = locate_data_dir()

pieces = { "wp": d+"images/white-pawn.png",
           "wn": d+"images/white-knight.png",
           "wb": d+"images/white-bishop.png",
           "wr": d+"images/white-rook.png",
           "wq": d+"images/white-queen.png",
           "wk": d+"images/white-king.png",
           "bp": d+"images/black-pawn.png",
           "bn": d+"images/black-knight.png",
           "bb": d+"images/black-bishop.png",
           "br": d+"images/black-rook.png",
           "bq": d+"images/black-queen.png",
           "bk": d+"images/black-king.png",
           'light-square': d+"images/light-square.png",
           'dark-square': d+"images/dark-square.png",
           'border': d+"images/border.png",
}

piece_surfaces = {}
for piece in pieces.keys():
    print "Loading " + pieces[piece]
    piece_surfaces[piece] = cairo.ImageSurface.create_from_png(pieces[piece])

def piece_handle_to_letter(handle, fen=False):
    if len(handle) == 0: return None

    handles = { "wp": "P", "bp": "P",
                "wn": "N", "bn": "N",
                "wb": "B", "bb": "B",
                "wr": "R", "br": "R",
                "wq": "Q", "bq": "Q",
                "wk": "K", "bk": "K" }
                
    if fen and handle[0] == "b":
        return handles[handle].lower()
    else:
        return handles[handle]
