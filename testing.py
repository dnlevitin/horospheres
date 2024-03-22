import unittest 
from rips_horosphere_generator import RipsHorosphereGenerator
from divergence_horosphere_generator import DivergenceHorosphereGenerator
from defining_data import WeirdGroupData, SierpinskiCarpetData, VirtualSurfaceData

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """

    def test_something(self):
        self.assertEqual(1, True)


    def test_virtual_surface_divergence_graph(self):
        Data = VirtualSurfaceData()
        HorosphereGenerator = DivergenceHorosphereGenerator(Data.c_map, Data.o_map, Data.ray)
        Graph = HorosphereGenerator.horosphere_as_networkx(3, 0)
        self.assertEqual(Graph.number_of_edges, Graph.number_of_nodes - 1) 