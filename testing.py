import unittest 
from rips_fsm_generator import RipsFSMGenerator
from rips_horosphere_generator import RipsHorosphereGenerator
from divergence_horosphere_generator import DivergenceHorosphereGenerator
import defining_data

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """

    def test_rips_FSMs(self):

        """
        Test that each machine has the right number of states and
        transitions.
        """

        # Case 1: the virtual surface group
        data = defining_data.VirtualSurfaceData()
        rips_fsm_generator = RipsFSMGenerator(data.c_map, data.o_map, data.ray)
        shortlex_machine = rips_fsm_generator.shortlex_machine()
        restricted_shortlex_machine = rips_fsm_generator.shortlex_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = rips_fsm_generator.geodesic_machine()
        restricted_geodesic_machine = rips_fsm_generator.geodesic_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = rips_fsm_generator.first_letter_excluder({'d'})
        shortlex_suffix_machine = rips_fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = rips_fsm_generator.geodesic_suffix_machine()
        self.assertEqual(len(shortlex_machine.states()), 8)
        self.assertEqual(len(shortlex_machine.transitions()), 24) 
        self.assertEqual(len(restricted_shortlex_machine.states()), 4)
        self.assertEqual(len(restricted_shortlex_machine.transitions()), 7)
        self.assertEqual(len(geodesic_machine.states()), 11)
        self.assertEqual(len(geodesic_machine.transitions()), 40)
        self.assertEqual(len(restricted_geodesic_machine.states()), 6)
        self.assertEqual(len(restricted_geodesic_machine.transitions()), 11)
        self.assertEqual(len(letter_excluder.states()), 2)
        self.assertEqual(len(letter_excluder.transitions()), 9)
        self.assertEqual(len(shortlex_suffix_machine.states()), 13)
        self.assertEqual(len(shortlex_suffix_machine.transitions()), 34)
        self.assertEqual(len(geodesic_suffix_machine.states()), 16)
        self.assertEqual(len(geodesic_suffix_machine.transitions()), 52)


        # Case 2: for the Sierpinski Carpet group.
        data = defining_data.SierpinskiCarpetData()
        rips_fsm_generator = RipsFSMGenerator(data.c_map, data.o_map, data.ray)
        shortlex_machine = rips_fsm_generator.shortlex_machine()
        restricted_shortlex_machine = rips_fsm_generator.shortlex_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = rips_fsm_generator.geodesic_machine()
        restricted_geodesic_machine = rips_fsm_generator.geodesic_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = rips_fsm_generator.first_letter_excluder({'d'})
        shortlex_suffix_machine = rips_fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = rips_fsm_generator.geodesic_suffix_machine()
        self.assertEqual(len(shortlex_machine.states()), 24)
        self.assertEqual(len(shortlex_machine.transitions()), 163)
        self.assertEqual(len(restricted_shortlex_machine.states()), 4)
        self.assertEqual(len(restricted_shortlex_machine.transitions()), 7)
        self.assertEqual(len(geodesic_machine.states()), 41)
        self.assertEqual(len(geodesic_machine.transitions()), 330)
        self.assertEqual(len(restricted_geodesic_machine.states()), 6)
        self.assertEqual(len(restricted_geodesic_machine.transitions()), 11)
        self.assertEqual(len(letter_excluder.states()), 2)
        self.assertEqual(len(letter_excluder.transitions()), 19)
        self.assertEqual(len(shortlex_suffix_machine.states()), 36)
        self.assertEqual(len(shortlex_suffix_machine.transitions()), 239)
        self.assertEqual(len(geodesic_suffix_machine.states()), 58)
        self.assertEqual(len(geodesic_suffix_machine.transitions()), 454)

        # Case 3: for the weird group.
        data = defining_data.WeirdGroupData()
        rips_fsm_generator = RipsFSMGenerator(data.c_map, data.o_map, data.ray)
        shortlex_machine = rips_fsm_generator.shortlex_machine()
        restricted_shortlex_machine = rips_fsm_generator.shortlex_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = rips_fsm_generator.geodesic_machine()
        restricted_geodesic_machine = rips_fsm_generator.geodesic_machine(
            restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = rips_fsm_generator.first_letter_excluder({'d'})
        shortlex_suffix_machine = rips_fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = rips_fsm_generator.geodesic_suffix_machine()
        self.assertEqual(len(shortlex_machine.states()), 12)
        self.assertEqual(len(shortlex_machine.transitions()), 77)
        self.assertEqual(len(restricted_shortlex_machine.states()), 4)
        self.assertEqual(len(restricted_shortlex_machine.transitions()), 8)
        self.assertEqual(len(geodesic_machine.states()), 34)
        self.assertEqual(len(geodesic_machine.transitions()), 238)
        self.assertEqual(len(restricted_geodesic_machine.states()), 5)
        self.assertEqual(len(restricted_geodesic_machine.transitions()), 10)
        self.assertEqual(len(letter_excluder.states()), 2)
        self.assertEqual(len(letter_excluder.transitions()), 17)
        self.assertEqual(len(shortlex_suffix_machine.states()), 21)
        self.assertEqual(len(shortlex_suffix_machine.transitions()), 129)
        self.assertEqual(len(geodesic_suffix_machine.states()), 50)
        self.assertEqual(len(geodesic_suffix_machine.transitions()), 338)

    def test_virtual_surface_rips_graph(self):
        
        """
        Test that the rips graph on the virtual surface group has the
        expected number of vertices and edges.
        """

        data = defining_data.VirtualSurfaceData()
        horosphere_generator = RipsHorosphereGenerator(
            data.c_map, data.o_map, data.ray)
        
        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        self.assertEqual(graph.number_of_nodes(), 29)
        self.assertEqual(graph.number_of_edges(), 51)

    def test_sierpinski_carpet_rips_graph(self):

        """
        Test that the rips graph on the virtual Sierpinski Carpet group
        has the expected number of edges and vertices.
        """

        data = defining_data.SierpinskiCarpetData()
        horosphere_generator = RipsHorosphereGenerator(
            data.c_map, data.o_map, data.ray)
        
        graph = horosphere_generator.horosphere_as_networkx(2, 0)
        self.assertEqual(graph.number_of_nodes(), 61)
        self.assertEqual(graph.number_of_edges(), 292)

    def test_theta_graph_rips_graph(self):

        """
        Test that the rips graph on the virtual branched surface group
        has the expected number of edges and vertices.
        """

        data = defining_data.ThetaGraphData()
        horosphere_generator = RipsHorosphereGenerator(
            data.c_map, data.o_map, data.ray)
        
        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        self.assertEqual(graph.number_of_nodes(), 362)
        self.assertEqual(graph.number_of_edges(), 1421)

    def test_theta_graph_divergence_graph(self):

        """
        Test that the divergence graph on the virtual branched surface
        group has the expected number of vertices and edges.
        """

        data = defining_data.ThetaGraphData()
        horosphere_generator = DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)
        
        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        self.assertEqual(graph.number_of_nodes(), 362)
        self.assertEqual(graph.number_of_edges(), 401)
        graph = horosphere_generator.horosphere_as_networkx(2, 0)
        self.assertEqual(graph.number_of_nodes(), 54)
        self.assertEqual(graph.number_of_edges(), 57)

    def test_virtual_surface_divergence_graph(self):
       
        """
        Test that the divergence graph on the virtual surface group is 
        a path as desired.
        """

        data = defining_data.VirtualSurfaceData()
        horosphere_generator = DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)

        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        #This graph is supposed to be a path.
        self.assertEqual(graph.number_of_edges(), graph.number_of_nodes() - 1)
        
    def test_almost_virtual_surface_divergence_graph(self):

        """
        Test that the divergence graph on the almost virtual surface
        group has the expected number of vertices and edges, as well as
        certain specific edges.
        """

        data = defining_data.AlmostVirtualSurfaceData()
        horosphere_generator = DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)

        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        assert('b' in list(graph.neighbors('a')))
        # Check a lengthening by 2
        assert('ab' in list(graph.neighbors('')))
        # Check an edge between words 4 letters apart
        assert('dab' in list(graph.neighbors('dfc')))
        self.assertEqual(graph.number_of_nodes(), 55)
        self.assertEqual(graph.number_of_edges(), 76)

    def test_weird_group_divergence_graph(self):

        """
        Test that the divergence graph on the weird group has the
        expected number of vertices and edges, and that certain edges
        are not present even though the words differ by a pair of
        commuting letters.
        """

        data=defining_data.WeirdGroupData()
        horosphere_generator = DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)

        graph = horosphere_generator.horosphere_as_networkx(2, 0)
        # Check the absence of certain edges even when the pairs of
        # words differ by a pair of commuting letters
        assert(not 'hz' in list(graph.neighbors('he')))
        assert(not 'b' in list(graph.neighbors('bd')))
        assert(not 'e' in list(graph.neighbors('c')))
        assert(not 'd' in list(graph.neighbors('e')))
        self.assertEqual(graph.number_of_nodes(), 49)
        self.assertEqual(graph.number_of_edges(), 69)