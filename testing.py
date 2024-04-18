import unittest 
from rips_horosphere_generator import RipsHorosphereGenerator
from divergence_horosphere_generator import DivergenceHorosphereGenerator
import defining_data

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """


    def test_virtual_surface_divergence_graph(self):
        data = defining_data.VirtualSurfaceData()
        HorosphereGenerator = defining_data.DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)

        graph = HorosphereGenerator.horosphere_as_networkx(3, 0)
        #This graph is supposed to be a path.
        self.assertEqual(graph.number_of_edges(), graph.number_of_nodes() - 1)