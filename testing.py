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

        #Case 1: the virtual surface group
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


        #Case 2: for the Sierpinski Carpet group.
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

        #Case 3: for the weird group.
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


    def test_virtual_surface_divergence_graph(self):
        data = defining_data.VirtualSurfaceData()
        horosphere_generator = DivergenceHorosphereGenerator(
            data.c_map, data.o_map, data.ray)

        graph = horosphere_generator.horosphere_as_networkx(3, 0)
        #This graph is supposed to be a path.
        self.assertEqual(graph.number_of_edges(), graph.number_of_nodes() - 1)