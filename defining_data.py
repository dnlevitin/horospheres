
class SierpinskiCarpetData:
    
    def __init__(self):

        self.c_map = {
            'a' : {'b', 'e', 'f', 'j'}, 'b' : {'a', 'c', 'f', 'g'},
            'c' : {'b', 'd', 'g', 'h'}, 'd' : {'c', 'e', 'h', 'i'},
            'e' : {'a', 'd', 'i', 'j'}, 'f' : {'a', 'b', 'g', 'j'},
            'g' : {'b', 'c', 'f', 'h'}, 'h' : {'c', 'd', 'g', 'i'},
            'i' : {'d', 'e', 'h', 'j'}, 'j' : {'a', 'e', 'f', 'i'}
        }

        self.o_map = {'a' : 0, 'b' : 1, 'c' : 2, 'd' : 3, 'e' : 4, 'f' : 5, 'g' : 6, 'h' : 7, 'i' : 8, 'j' : 9}

        self.ray = ('a', 'g')

class VirtualSurfaceData:

    def __init__(self):
        self.c_map = {'a': {'b', 'e'}, 'b': {'a', 'c'}, 'c': {'b', 'd'}, 'd': {'e', 'c'}, 'e': {'a', 'd'}}
        self.o_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        self.ray = ('a', 'c')

class WeirdGroupData:

    def __init__(self):
        self.c_map = {
            'a': {'b', 'g', 'h'}, 'b': {'a', 'z'}, 'c': {'d', 'e', 'g', 'z'}, 'd': {'c', 'e', 'f', 'z'},
            'e': {'c', 'd', 'f', 'z'}, 'f': {'d', 'e', 'h', 'z'}, 'g': {'a', 'c'}, 'h': {'a', 'f'}, 'z': {'b', 'c', 'd', 'e', 'f'} 
            }

        self.o_map = {
            'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'z': 8
            }

        self.ray = ('a', 'z')
