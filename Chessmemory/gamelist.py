import gtk
import PGN

class GameList(gtk.TreeView):
    def __init__(self, window):
        self.parent_window = window
        self.games = []
    
        gtk.TreeView.__init__(self)
        
        self.connect("row-activated", self.on_row_activated)
        
        self.set_rules_hint(True)
        self.set_enable_search(False)
        
        self.store = gtk.ListStore(int, int, str)
        self.set_model(self.store)
        
        column_line = gtk.TreeViewColumn('Line')
        column_line.set_resizable(True)
        column_score = gtk.TreeViewColumn('Score')
        column_score.set_resizable(True)
        column_moves = gtk.TreeViewColumn('Moves')
        column_moves.set_resizable(True)
        
        self.append_column(column_line)
        self.append_column(column_score)
        self.append_column(column_moves)
        
        cell = gtk.CellRendererText()
        column_line.pack_start(cell, True)
        column_line.add_attribute(cell, 'text', 0)
        column_score.pack_start(cell, True)
        column_score.add_attribute(cell, 'text', 1)
        column_moves.pack_start(cell, True)
        column_moves.add_attribute(cell, 'text', 2)
        
    def load(self, filename):
        self.store.clear()
        for game in PGN.parse(filename):
            self.games.append(game)
            line_state = 0
            if self.parent_window.data.line_state.has_key(game.index):
                line_state = self.parent_window.data.line_state[game.index]
            self.store.append([game.index, line_state, "Moves"])
        
        self.set_cursor(0)
        self.columns_autosize()
        
    def on_row_activated(self, widget, path, col):
        self.parent_window.open_game(self.games[self.store[path][0]])
        
