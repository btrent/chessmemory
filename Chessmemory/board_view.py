# Graphical display of a board, using a Board object as its model.

import gtk
import gtk.gdk
import gobject
import time
import copy
import cairo

from pieces import piece_surfaces
from square_utils import *
from board import Board
from utils import locate_data_dir

ANIMATION_TIME = 0.15

class Piece:
    def _get_coords(self):
        return self._coords
    coords = property(_get_coords)
    
    def _get_last_coords(self):
        return self._last_coords
    last_coords = property(_get_last_coords)
    
    def _get_square(self):
        return self._square
    square = property(_get_square)
    
    def _get_piece_id(self):
        return self._piece_id
    piece_id = property(_get_piece_id)
    
    def _get_opacity(self):
        return self._opacity
    opacity = property(_get_opacity)
    
    def get_dirty(self):
        return self._dirty
    def set_dirty(self, value):
        self._dirty = value
        
    def get_moving(self):
        return self._moving

    def __init__(self, square, piece_id):
        self._square = square
        self._piece_id = piece_id
        
        self._update_file_rank()
        
        # Coordinates in relative values (0.0 to 1.0)
        self._start = self._fyle * (1.0/8), self._rank * (1.0/8)
        self._destination = self._start
        self._coords = self._start
        
        self._start_opacity = 0.0
        self._destination_opacity = 1.0
        self._opacity = 0.0
        
        self._last_coords = self._start
        self._last_opacity = 0.0
        self._dirty = True
        self._moving = False
        
    def reset_start(self):
        self._start = self._coords
        self._start_opacity = self._opacity
    
    def update_for_alpha(self, alpha):
        self._last_coords = copy.copy(self._coords)
        self._last_opacity = copy.copy(self._opacity)
        
        (sx, sy) = self._start
        (dx, dy) = self._destination    
        self._coords = (sx+((dx-sx)*alpha), sy+((dy-sy)*alpha))
        if self._coords == self._destination:
            self._start = self._coords
        
        (so, do) = self._start_opacity, self._destination_opacity
        self._opacity = so+((do-so)*alpha)
        if self._opacity == self._destination_opacity:
            self._start_opacity = self._opacity
            
        if ( self._last_coords != self._coords or self._last_opacity != self._opacity ):
            self._dirty = True
        else:
            self._moving = False
        
    def set_opacity(self, opacity):
        self._start_opacity = self._opacity
        self._destination_opacity = opacity
        self._dirty = True
        
    def move_to(self, dest_square):
        self._destination = square_file(dest_square) * (1.0/8), square_rank(dest_square) * (1.0/8)
        self._square = dest_square
        self._destination_opacity = 1.0
        self._update_file_rank()
        self._moving = True
        self._dirty = True
        
    def _update_file_rank(self):
        self._fyle = square_file(self._square)
        self._rank = square_rank(self._square)    


class BoardView(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }
    
    
    def _get_board(self):
        return self._board
    board = property(_get_board)
    
    
    def __init__(self, boardwindow):
        gtk.DrawingArea.__init__(self)
        self.boardwindow = boardwindow
        self.set_events(gtk.gdk.SCROLL_MASK)
        
        self._width = 360
        self._old_width = self._width
        self.set_size_request(self._width, self._width)
        
        self._flipped = False
        self._enable_animations = True
        self._draw_coordinates = True
        
        self._animation_timeout = None
        self._animation_scale = 1.0
        self._animation_time = time.time() + ANIMATION_TIME*self._animation_scale
        
        self._pieces = []
        self._piece_spool = []
        
        self._board_buffer = None
        self._buffer_size = (0, 0)
        self._draw_buffer = None
        self._dirty = False
        
        self._board = Board(self)
        self.update()
        
        self._board.connect('position-changed-event', self.position_changed_event)
        self.connect('scroll-event', self.scroll_event)
        
    
    def _create_context(self):
        cr = self.window.cairo_create()
        return cr
        
        
    def do_expose_event(self, event):
        self._resize()
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self._draw(cr, *self.window.get_size())
        
        
    def update(self):    
        self._piece_spool = self._pieces
        self._pieces = []
        
        static_pieces = []
        moving_pieces = []
        
        for i in range(64):
            if self._board.squares[i]:
                piece = self._grab_piece(i, self._board.squares[i])
                
                # make sure moving pieces end up on top
                if ( piece.get_moving() ):
                    moving_pieces.append(piece)
                else:
                    static_pieces.append(piece)
                    
        # Let the remaining pieces fade out
        for piece in self._piece_spool:
            piece.set_opacity(0.0)
            piece.square = -1
            self._pieces.append(piece)
            
        self._pieces += static_pieces + moving_pieces
            
        for piece in self._pieces:
            piece.reset_start()
            
        self._animation_time = time.time()
        self._animation_id = gobject.idle_add(self._run_animation)


    def _grab_piece(self, square, piece_id):
        """Find a suitable piece or create a new one."""
        for piece in self._piece_spool:
            if piece.square == square and piece.piece_id == piece_id:
                self._piece_spool.remove(piece)
                return piece
                
        # Try to find a "free" piece of the same type and move it
        for piece in self._piece_spool:
            if piece.piece_id == piece_id and self._board.squares[piece.square] != piece_id and piece.square != -1:
                self._piece_spool.remove(piece)
                piece.move_to(square)
                return piece
        
        piece = Piece(square, piece_id)
        return piece

    def flip(self):
        self._flipped = not self._flipped
        self.queue_draw()
        
    def toggle_coordinates(self):
        self._draw_coordinates = not self._draw_coordinates
        self._dirty = True
        self.queue_draw()
        
    def save_png(self, filename):
        """Draw the board view to a PNG surface and save it to filename."""
        image = cairo.ImageSurface(cairo.FORMAT_ARGB32, self._width, self._width)
        cr = cairo.Context(image)
        self._draw(cr, self._width, self._width)
        image.write_to_png(filename)
    
    def _draw_board(self, cr, size, border):
        borderpx = int(size*border)    

        # Calculate sizes for an even square size for sharp intersections
        boardsize = size - (borderpx * 2)
        sw = int(boardsize / 8)
        boardsize = sw * 8
        fullsize = boardsize + (borderpx * 2)
        
        cr.set_line_width(1)
        
        cr.save()
        
        w = fullsize
        
        # Draw border background
        image = piece_surfaces['border']
        cr.rectangle(0, 0, w, w)
        cr.set_source_surface(image, 0, 0)
        pattern = cr.get_source()
        pattern.set_extend(cairo.EXTEND_REPEAT)
        cr.fill()
        
        # Draw outline
        cr.rectangle(0.5, 0.5, w-1, w-1)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.stroke()
        
        # Draw inside shadows
        cr.move_to(1.5, w-1.5)
        cr.line_to(1.5, 1.5)
        cr.line_to(w-1.5, 1.5)
        cr.set_source_rgba(1, 1, 1, 0.2)
        cr.stroke()
        cr.move_to(w-1.5, 1.5)
        cr.line_to(w-1.5, w-1.5)
        cr.line_to(1.5, w-1.5)
        cr.set_source_rgba(0, 0, 0, 0.3)
        cr.stroke()
        
        # Draw inside border
        cr.rectangle(borderpx-0.5, borderpx-0.5, w-2*borderpx+1, w-2*borderpx+1)
        cr.set_source_rgba(0, 0, 0, 0.2)
        cr.stroke()
            
        cr.translate(borderpx, borderpx)
        w = boardsize
        
        # Draw Coordinates
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] 
        lines = ['1', '2', '3', '4', '5', '6', '7', '8']
        if self._draw_coordinates:
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(borderpx*0.6)
            cr.set_source_rgba(1, 1, 1)
            cr.move_to(borderpx*0.2, borderpx*2)
            cr.show_text('A')
            
            if self._flipped:
                i = 7
            else:
                i = 0
            for row in rows:
                fw = cr.text_extents(row)[2]
                fh = cr.text_extents(row)[3]
                cr.move_to(sw*i + sw/2 - fw/2, w + borderpx*0.5 + fh/2)
                cr.show_text(row)
                if self._flipped:
                    i -= 1
                else:
                    i += 1
            # END for
                
            if self._flipped:
                i = 0
            else:
                i = 7
            for line in lines:
                fw = cr.text_extents(line)[2]
                fh = cr.text_extents(line)[3]
                cr.move_to(0-borderpx*0.55 - fw/2, sw*i + sw/2 + fh/2)
                cr.show_text(line)
                if self._flipped:
                    i += 1
                else:
                    i -= 1
            # END for
                
        # Draw the squares
        odd = True
        for i in range(8):
            for j in range(8):
                if odd:
                    image = piece_surfaces['light-square']
                    cr.save()
                    cr.translate(sw*i, sw*j)
                    cr.scale(1.0*sw/image.get_width(), 1.0*sw/image.get_height())
                    cr.set_source_surface(image, 0, 0)
                    cr.paint()
                    cr.restore()
                else:
                    image = piece_surfaces['dark-square']
                    cr.save()
                    cr.translate(sw*i, sw*j)
                    cr.scale(1.0*sw/image.get_width(), 1.0*sw/image.get_height())
                    cr.set_source_surface(image, 0, 0)
                    cr.paint()
                    cr.restore()
                odd = not odd
            odd = not odd
    # END _draw_board
    
    
    def _draw(self, cr, width, height, redraw = True):
        t1 = time.time()
    
        PADDING = 3    
        size = min(width, height) - PADDING * 2

        if self._draw_coordinates:
            border = 0.04
        else:
            border = 0.02            
        borderpx = int(size*border)
        
        # Calculate sizes for an even square size for sharp intersections
        boardsize = size - (borderpx * 2)
        sw = int(boardsize / 8)
        boardsize = sw * 8
        fullsize = boardsize + (borderpx * 2)
        
        # Horizontally center the board
        cr.translate(int((width - (fullsize + 2 * PADDING)) / 2), 0)
        cr.translate(PADDING, PADDING)
        
        self._draw_buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        draw_context = cairo.Context(self._draw_buffer)
        draw_context.set_line_width(1)
        
        # Create a new board when necessary
        if self._buffer_size != (width, height) or not self._board_buffer or self._dirty:
            self._board_buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
            cr2 = cairo.Context(self._board_buffer)
            self._draw_board(cr2, size, border)
            self._buffer_size = (width, height)
            self._dirty = False
        
        # Piece animation
        alpha = min(1.0, (time.time() - self._animation_time) / (ANIMATION_TIME*self._animation_scale))
        for piece in self._pieces:
            piece.update_for_alpha(alpha)
        
        if (redraw):
            draw_context.set_source_surface(self._board_buffer)
            draw_context.paint()
        else:
            # Redraw only damaged areas
            draw_context.set_source_surface(self._board_buffer)
            clip = False
            
            for piece in self._pieces:
                if (piece.get_dirty()):
                    clip = True
                    (x, y) = self._rotate_coordinates(piece.coords)
                    cr.rectangle(boardsize*x+borderpx, boardsize*y+borderpx, sw, sw)
                    (x, y) = self._rotate_coordinates(piece.last_coords)
                    cr.rectangle(boardsize*x+borderpx, boardsize*y+borderpx, sw, sw)
                    piece.set_dirty(False)
            # END for
            if (clip):
                cr.clip ()
            else:
                return    
            #return
            draw_context.set_source_surface(self._board_buffer)
            draw_context.paint()
        
        draw_context.translate(borderpx, borderpx)
        
        for piece in self._pieces:
            #if ( not redraw and not piece._get_dirty() ):
            #    continue
            #else:
            #    piece._set_dirty(False)
            
            # Get rid of faded pieces
            if piece.square == -1 and piece.opacity <= 0:
                self._pieces.remove(piece)
                continue
            
            image = piece_surfaces[piece.piece_id]
            (x, y) = self._rotate_coordinates(piece.coords)
            draw_context.save()
            draw_context.rectangle(boardsize*x, boardsize*y, sw, sw)
            draw_context.clip()
            
            draw_context.translate(boardsize*x, boardsize*y)
            draw_context.scale(1.0*sw/image.get_width(), 1.0*sw/image.get_height())
            draw_context.set_source_surface(image, 0, 0)
            draw_context.paint_with_alpha(piece.opacity)
            draw_context.restore()
        # END for
        
        cr.set_source_surface(self._draw_buffer)
        cr.paint()
        
        #print "drawing time: " + str(time.time() - t1)
    # END _draw
        
            
    def _run_animation(self):
        alpha = min(1.0, (time.time() - self._animation_time) / (ANIMATION_TIME*self._animation_scale))
        cr = self.window.cairo_create()
        self._draw(cr, redraw = False, *self.window.get_size())
        
        if (alpha >= 1.0):
            return False
        return True


    def _calculate_width(self):
        wallocation = self.boardwindow.window.get_allocation()
        allocation = self.get_allocation()
        min_width = 160
        max_width = int(wallocation.height / 8) * 8 - 160
        width = int(allocation.width / 8) * 8
        return max(min(width, max_width), min_width) + 1

        
    def _resize(self):
        self._width = self._calculate_width()
        if self._width == self._old_width:
            return
        self.set_size_request(self._width, self._width)
        self._old_width = self._width
    
    
    # Return relative coordinates for piece drawing, depending on board rotation
    def _rotate_coordinates(self, coords):
        x, y = coords
        d = 1.0 / 8 * 7
        if self._flipped:
            return d - x, y
        else:
            return x, d - y


    def scroll_event(self, sender, event):
        # Yes this is opposite to how scid does it, but more intuitive
        if event.direction == gtk.gdk.SCROLL_DOWN:
            self._board.move_back()
        elif event.direction == gtk.gdk.SCROLL_UP:
            self._board.move_forward()

    
    def position_changed_event(self, sender, position):
        self.update()
    
