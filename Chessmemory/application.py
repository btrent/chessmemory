import utils
from mainwindow import MainWindow
from ECO import ECO

class Application:
    def __init__(self, filename=""):
        self.eco = ECO(utils.locate_data_dir() + "eco.positions")
        mainwindow = MainWindow(self)        
        if filename:
            mainwindow.load_games(filename)    
