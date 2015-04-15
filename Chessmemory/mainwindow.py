# coding: utf-8

import datetime
import gtk
import gtk.glade
import os
import pickle
import sys

import utils
import PGN
from random import randrange

from board_view import BoardView
from gamelist import GameList
from ECO import ECO
from notation_view import NotationView

class MainWindow:
    def __init__(self, app):
        self.app = app
        self.filename = ""
        self.data = Data()
        self.current_game = 0

        self.UNSEEN_SCORE = 0
        self.DONT_KNOW_SCORE = 1
        self.FUZZY_SCORE = 2
        self.GOT_IT_SCORE = 3
    
        widgets = gtk.glade.XML(utils.locate_data_dir() + "chessmemory.glade")
        widgets.signal_autoconnect(self)
        
        self.window = widgets.get_widget("mainwindow")
        self.boardbox = widgets.get_widget("alignment_board_display")
        self.hpane = widgets.get_widget("hpane")
        self.vpane = widgets.get_widget("vpane")
        
        self.hpane.set_position(680)
        self.vpane.set_position(350)

        self.window.set_size_request(1440, 800)

        self.window.connect("key_press_event", self.key_press_event)
        self.window.set_events(gtk.gdk.KEY_PRESS_MASK)
        
        try:
            icon = gtk.icon_theme_get_default().load_icon("chessmemory", 48, 0)
            self.window.set_icon(icon)
        except:
            print "Warning:", sys.exc_info()[1]
                    
        # Move control buttons
        self.button_move_first = widgets.get_widget("button_move_first")
        self.button_move_back = widgets.get_widget("button_move_back")
        self.button_move_takeback = widgets.get_widget("button_move_takeback")
        self.button_move_forward = widgets.get_widget("button_move_forward")
        self.button_move_last = widgets.get_widget("button_move_last")
        self.button_dont_know = widgets.get_widget("button_dont_know")
        self.button_fuzzy = widgets.get_widget("button_fuzzy")
        self.button_got_it = widgets.get_widget("button_got_it")
        
        self.boardview = BoardView(self)
        #self.board = self.boardview.board
        self.boardbox.add(self.boardview)
        
        self.boardview.board.connect('position-changed-event', self.position_changed_event)
        
        self.notationview = NotationView()
        self.notationview.board = self.boardview.board
        self.boardview.board.connect('position-changed-event', self.notationview.position_changed_event) 
        widgets.get_widget('sw_notation').add(self.notationview)
        
        self.gamelist = GameList(self)
                
        #self.notebook = gtk.Notebook()
        #widgets.get_widget("notebook_box").add(self.notebook)
        #self.notebook.append_page(self.gamelist)
        widgets.get_widget("sw_gamelist").add(self.gamelist)
        
        self.window.show_all()        
        self.button_move_takeback.hide() # TODO: reconsider
        
    def on_resize(self, widget):
        #self.boardview.on_resize()
        pass
        
    def on_rotate(self, widget):
        self.boardview.flip()

    def key_press_event(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval) == "Right":
            self.boardview.board.move_forward()
        elif gtk.gdk.keyval_name(event.keyval) == "Left":
            self.boardview.board.move_back()
        elif gtk.gdk.keyval_name(event.keyval) == "question":
            self.load_random_game()
        elif gtk.gdk.keyval_name(event.keyval) == "Return":
            self.on_button_got_it_clicked(self)
        elif gtk.gdk.keyval_name(event.keyval) == "space":
            self.on_button_fuzzy_clicked(self)
        elif gtk.gdk.keyval_name(event.keyval) == "Shift_L":
            self.on_button_dont_know_clicked(self)

    def on_show_coordinates_toggle(self, widget):
        self.boardview.toggle_coordinates()
    
    def on_button_move_back_clicked(self, widget):
        self.boardview.board.move_back()
    
    def on_button_move_forward_clicked(self, widget):
        self.boardview.board.move_forward()
        
    def on_button_move_first_clicked(self, widget):
        self.boardview.board.move_first()
    
    def on_button_move_last_clicked(self, widget):
        self.boardview.board.move_last()

    def on_button_dont_know_clicked(self, widget):
        self.data.set_score(self.current_game, self.DONT_KNOW_SCORE)
        self.gamelist.store[self.current_game][1] = self.DONT_KNOW_SCORE
        self.save_state()
        self.load_random_game()
        
    def on_button_fuzzy_clicked(self, widget):
        self.data.set_score(self.current_game, self.FUZZY_SCORE)
        self.gamelist.store[self.current_game][1] = self.FUZZY_SCORE
        self.save_state()
        self.load_random_game()
        
    def on_button_got_it_clicked(self, widget):
        self.data.set_score(self.current_game, self.GOT_IT_SCORE)
        self.gamelist.store[self.current_game][1] = self.GOT_IT_SCORE
        self.save_state()
        self.load_random_game()
        
    def load_random_game(self):
        random_index = randrange(0,len(self.gamelist.games))
        self.open_game(self.gamelist.games[random_index])

    def save_state(self):
        save_filename = self.filename + ".dat"
        f = open(save_filename, 'w')
        pickle.dump(self.data, f)

    def load_state(self):
        load_filename = self.filename + ".dat"
        try:
            f = open(load_filename)
            unpickler = pickle.Unpickler(f)
            self.data = unpickler.load()
        except:
            pass

    def open_game(self, game):
        game.notation.nodes = PGN.parse_string(game.notation_string)
        self.boardview.board.set_game(game)
        #self.boardview.update()
        self.notationview.update()
        self.current_game = game.index
        self.gamelist.set_cursor(game.index)
        self.data.inc_seen()

        # TODO P3: check for list of player names
        if game.keys['Black'] == 'Player' and self.boardview._flipped is False:
            self.boardview.flip()
        
    def load_games(self, filename):
        self.filename = filename
        self.load_state()
        self.gamelist.load(filename)
        #self.open_game(self.gamelist.games[0])
        self.load_random_game()
        filebase = os.path.splitext(os.path.basename(filename))[0]
        self.window.set_title(filebase)
        
    def on_open(self, sender):
        fc = gtk.FileChooserDialog(title="Open", parent=self.window,
                                   buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                            gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        if self.filename:
            fc.set_filename(self.filename)
        result = fc.run()
        fc.hide()
        if result == gtk.RESPONSE_ACCEPT:
            self.load_games(fc.get_filename())
            
    def on_save_board_image(self, sender):
        fc = gtk.FileChooserDialog(title="Save Image", parent=self.window,
                                   action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                   buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                            gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        result = fc.run()
        fc.hide()
        if result == gtk.RESPONSE_ACCEPT:
            self.boardview.save_png(fc.get_filename())
            
    def on_about(self, sender):
        ad = gtk.AboutDialog()
        ad.set_name("Chessmemory")
        ad.set_comments("Open Source Chess Viewer and Database Tool")
        ad.set_version(utils.get_version())
        ad.set_copyright("Copyright © 2006 Daniel Borgmann")
        ad.set_authors([
            "Daniel Borgmann <daniel.borgmann@gmail.com>",
            "Nils R Grotnes <nils.grotnes@gmail.com>",
        ])
        ad.set_license(utils.get_license())
        ad.set_logo_icon_name("chessmemory")
        ad.run()
        
    def on_close(self, sender=None, event=None):
        gtk.main_quit()
            
    def position_changed_event(self, sender, new_position=None):
        print self.app.eco.get_name(new_position.get_FEN())
    
class Data:

    today = None
    line_state = None
    seen_today = 0
    seen_ever = 0

    def __init__(self, **kwargs):
        self.line_state = dict()
        self.today = datetime.date.today().isoformat()

    def inc_seen(self):
        self.seen_ever = self.seen_ever + 1
        curdate = datetime.date.today().isoformat()

        if curdate == self.today:
            self.seen_today = self.seen_today + 1
        else:
            self.today = curdate
            self.seen_today = 1

        print "Seen ever: " + str(self.seen_ever)
        print "Seen today: " + str(self.seen_today)

    def set_score(self, game_number, score):
        self.line_state[game_number] = score
