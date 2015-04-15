import PGN

class ECO:
    def __init__(self, filename):
        self.nodes = {}
        self.parse(filename)

    def parse(self, filename):
        ecofile = open(filename,'r',1)
        for line in ecofile:
            (fen, eco, name) = line.split('  ')
            node = {}
            node['eco'] = eco
            node['name'] = name
            self.nodes[fen] = node
            
    def get_eco(self, fen):
        try:
            return self.nodes[fen]['eco']
        except KeyError:
            return None
    
    def get_name(self, fen):
        try:
            return self.nodes[fen]['name']
        except KeyError:
            return None
    