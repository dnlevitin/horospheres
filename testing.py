import unittest 
from rips_fsm_generator import Rips_FSM_Generator
from divergence_fsm_generator import Divergence_FSM_Generator
from rips_horosphere_generator import RipsHorosphereGenerator
from divergence_horosphere_generator import DivergenceHorosphereGenerator
from defining_data import WeirdGroupData, SierpinskiCarpetData, VirtualSurfaceData

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """

    '''
    def test_virtual_surface_divergence_graph_mockup(self):
        #I am getting a strange error in processing a specific stage in test_virtual_surface_divergence_graph.
        Data = VirtualSurfaceData()
        HorosphereGenerator = DivergenceHorosphereGenerator(Data.c_map, Data.o_map, Data.ray)
        SuspectMachine = HorosphereGenerator.same_length_edge_checker1256
        #Check that there are no branches
        assert(SuspectMachine.is_deterministic())
        #Check that there are no epsilon transitions
        assert(transition.word_in[0] != None for transition in SuspectMachine.iter_transitions())
        #Check that there is a unique starting state.
        assert(len(SuspectMachine.initial_states()) == 1)
        #Check that each stage of the input can be processed.
        FirstTransitionIter = SuspectMachine.iter_transitions(SuspectMachine.initial_states()[0])
        FirstLabelList = [transition.word_in[0] for transition in FirstTransitionIter]
        assert(any(label == 'b+b' for label in FirstLabelList))
        #The bug appears in the following line, which represents a step that occurs in processing the first input.
        #In this version, we get the ValueError State ((), (), (), (), (), (), (), (), (), ('a', 'b', 'd', 'e', 'c'), (1, 1), True) does not belong to a finite state machine while checking epsilon successors
        SecondState = SuspectMachine.process(['b+b'])[1]
        #In this version, we get the AttributeError 'FSMState' object has no attribute 'transitions'
        #SecondState = SuspectMachine.process([('b', 'b')], check_epsilon_transitions = False)[1]
        SecondTransitionIter = SuspectMachine.iter_transitions(SecondState)
        SecondLabelList = [transition.word_in[0] for transition in SecondTransitionIter]
        assert(any(label == 'e+d' for label in SecondLabelList))
        ThirdState = SuspectMachine.process(['b+b', 'e+d'])[1]
        ThirdTransitionIter = SuspectMachine.iter_transitions(ThirdState)
        ThirdLabelList = [transition.word_in[0] for transition in ThirdTransitionIter]
        assert(any(label == '-+-' for label in ThirdLabelList))
        #Check that the final state is accepted as is expected.
        assert(SuspectMachine.process( ['b+b', 'e+d', '-+-'])[0])
    '''
        
    def  test_rips_fsms(self):
        #Check the numbers of states and transitions in some of the machines that Rips_FSM_Generator can produce.

        #Case 1: for the virtual surface group
        Data = VirtualSurfaceData()
        fsm_generator = Rips_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine()
        restricted_shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine(restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine()
        restricted_geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine(restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = fsm_generator._Rips_FSM_Generator__first_letter_excluder({'d'})
        shortlex_suffix_machine = fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = fsm_generator.geodesic_suffix_machine()
        assert(len(shortlex_machine.states) == 8)
        assert(len(shortlex_machine.transitions()) == 24)
        assert(len(restricted_shortlex_machine.states) == 4)
        assert(len(restricted_shortlex_machine.transitions()) == 7)
        assert(len(geodesic_machine.states) == 16)
        assert(len(geodesic_machine.transitions()) == 60)
        assert(len(restricted_geodesic_machine.states) == 8)
        assert(len(restricted_geodesic_machine.transitions()) == 15)
        assert(len(letter_excluder.states) == 2)
        assert(len(letter_excluder.transitions()) == 9)
        assert(len(shortlex_suffix_machine.states) == 13)
        assert(len(shortlex_suffix_machine.transitions()) == 34)
        assert(len(geodesic_suffix_machine.states) == 18)
        assert(len(geodesic_suffix_machine.transitions()) == 58)

        #Case 2: for the Sierpinski Carpet group.
        Data = SierpinskiCarpetData()
        fsm_generator = Rips_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine()
        restricted_shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine(restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine()
        restricted_geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine(restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = fsm_generator._Rips_FSM_Generator__first_letter_excluder({'d'})
        shortlex_suffix_machine = fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = fsm_generator.geodesic_suffix_machine()
        assert(len(shortlex_machine.states) == 24)
        assert(len(shortlex_machine.transitions()) == 163)
        assert(len(restricted_shortlex_machine.states) == 4)
        assert(len(restricted_shortlex_machine.transitions()) == 7)
        assert(len(geodesic_machine.states) == 51)
        assert(len(geodesic_machine.transitions()) == 420)
        assert(len(restricted_geodesic_machine.states) == 8)
        assert(len(restricted_geodesic_machine.transitions()) == 15)
        assert(len(letter_excluder.states) == 2)
        assert(len(letter_excluder.transitions()) == 19)
        assert(len(shortlex_suffix_machine.states) == 36)
        assert(len(shortlex_suffix_machine.transitions()) == 239)
        assert(len(geodesic_suffix_machine.states) == 64)
        assert(len(geodesic_suffix_machine.transitions()) == 504)

        #Case 3: for the weird group.
        Data = WeirdGroupData()
        fsm_generator = Rips_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine()
        restricted_shortlex_machine = fsm_generator._Rips_FSM_Generator__shortlex_machine(restricted_alphabet = {'a', 'b', 'c'})
        geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine()
        restricted_geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine(restricted_alphabet = {'a', 'b', 'c'})
        letter_excluder = fsm_generator._Rips_FSM_Generator__first_letter_excluder({'d'})
        shortlex_suffix_machine = fsm_generator.shortlex_suffix_machine()
        geodesic_suffix_machine = fsm_generator.geodesic_suffix_machine()
        assert(len(shortlex_machine.states) == 12)
        assert(len(shortlex_machine.transitions()) == 77)
        assert(len(restricted_shortlex_machine.states) == 4)
        assert(len(restricted_shortlex_machine.transitions()) == 8)
        assert(len(geodesic_machine.states) == 43)
        assert(len(geodesic_machine.transitions()) == 310)
        assert(len(restricted_geodesic_machine.states) == 8)
        assert(len(restricted_geodesic_machine.transitions()) == 16)
        assert(len(letter_excluder.states) == 2)
        assert(len(letter_excluder.transitions()) == 17)
        assert(len(shortlex_suffix_machine.states) == 21)
        assert(len(shortlex_suffix_machine.transitions()) == 129)
        assert(len(geodesic_suffix_machine.states) == 56)
        assert(len(geodesic_suffix_machine.transitions()) == 380)

    def test_divergence_fsms(self):
        #Check the numbers of states and transitions in some of the machines that Divergence_FSM_Generator can produce.
        #The current outputs suggest, for reasons I do not understand, that a lot of the machines have the same size
        #In particular, they suggest that edge_machine_1256 always has the same size as edge_machine_different_length.
        #I should check (a) that this reverses if I flip the order of the ray, and (b) that there's some a priori reason this should be true.

        #Case 1: for the virtual surface group
        Data = VirtualSurfaceData()
        fsm_generator = Divergence_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        horocyclic_suffix_machine_1234 = fsm_generator.horocyclic_suffix_machine_1234()
        horocyclic_suffix_machine_1256 = fsm_generator.horocyclic_suffix_machine_1256()
        SubwordDict1234 = {}
        SubwordDict1256 = {}
        SubwordDictDifferentLength = {}
        for letter in Data.c_map[Data.ray[0]].intersection(fsm_generator.lesser_star[Data.ray[1]]):
            SubwordDict1234[letter] = 1
            SubwordDict1256[letter] = 1
            SubwordDictDifferentLength[letter] = 1
        for letter in fsm_generator.lesser_star[Data.ray[0]].intersection(fsm_generator.greater_star[Data.ray[1]]):
            SubwordDict1234[letter] = 2
            SubwordDict1256[letter] = 2
            SubwordDictDifferentLength[letter] = 2
        for letter in fsm_generator.lesser_star[Data.ray[1]].difference(Data.c_map[Data.ray[0]]):
            SubwordDict1234[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[1]].union(fsm_generator.lesser_star[Data.ray[0]].intersection(Data.c_map[Data.ray[1]]))):
            SubwordDict1234[letter] = 4
        for letter in fsm_generator.lesser_star[Data.ray[0]].difference(Data.c_map[Data.ray[1]]):
            SubwordDict1256[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[0]].union(fsm_generator.lesser_star[Data.ray[1]].intersection(Data.c_map[Data.ray[0]]))):
            SubwordDict1256[letter] = 4
        for letter in fsm_generator.alphabet:
            try:
                SubwordDictDifferentLength[letter]
            except KeyError:
                SubwordDictDifferentLength[letter] = 3

        horocyclic_edge_machine_1234 = fsm_generator.horocyclic_edge_checker(SubwordDict1234)
        horocyclic_edge_machine_1256 = fsm_generator.horocyclic_edge_checker(SubwordDict1256)
        horocyclic_edge_machine_different_length = fsm_generator.horocyclic_edge_checker(SubwordDictDifferentLength)
        
        assert(len(horocyclic_suffix_machine_1234.states) == 13)
        assert(len(horocyclic_suffix_machine_1234.transitions()) == 34)
        assert(len(horocyclic_suffix_machine_1256.states) == 13)
        assert(len(horocyclic_suffix_machine_1256.transitions()) == 34)
        for state in horocyclic_edge_machine_1234.states:
            print(state.label)
        for transition in horocyclic_edge_machine_1234.transitions():
            print(transition)
        assert(len(horocyclic_edge_machine_1234.states) == 34)
        assert(len(horocyclic_edge_machine_1234.transitions()) == 83)
        assert(len(horocyclic_edge_machine_1256.states) == 34)
        assert(len(horocyclic_edge_machine_1256.transitions()) == 83)
        assert(len(horocyclic_edge_machine_different_length.states) == 34)
        assert(len(horocyclic_edge_machine_different_length.transitions()) == 83)

        #Case 2: for the Sierpisnki Carpet group
        Data = SierpinskiCarpetData()
        fsm_generator = Divergence_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        horocyclic_suffix_machine_1234 = fsm_generator.horocyclic_suffix_machine_1234()
        horocyclic_suffix_machine_1256 = fsm_generator.horocyclic_suffix_machine_1256()
        SubwordDict1234 = {}
        SubwordDict1256 = {}
        SubwordDictDifferentLength = {}
        for letter in Data.c_map[Data.ray[0]].intersection(fsm_generator.lesser_star[Data.ray[1]]):
            SubwordDict1234[letter] = 1
            SubwordDict1256[letter] = 1
            SubwordDictDifferentLength[letter] = 1
        for letter in fsm_generator.lesser_star[Data.ray[0]].intersection(fsm_generator.greater_star[Data.ray[1]]):
            SubwordDict1234[letter] = 2
            SubwordDict1256[letter] = 2
            SubwordDictDifferentLength[letter] = 2
        for letter in fsm_generator.lesser_star[Data.ray[1]].difference(Data.c_map[Data.ray[0]]):
            SubwordDict1234[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[1]].union(fsm_generator.lesser_star[Data.ray[0]].intersection(Data.c_map[Data.ray[1]]))):
            SubwordDict1234[letter] = 4
        for letter in fsm_generator.lesser_star[Data.ray[0]].difference(Data.c_map[Data.ray[1]]):
            SubwordDict1256[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[0]].union(fsm_generator.lesser_star[Data.ray[1]].intersection(Data.c_map[Data.ray[0]]))):
            SubwordDict1256[letter] = 4
        for letter in fsm_generator.alphabet:
            try:
                SubwordDictDifferentLength[letter]
            except KeyError:
                SubwordDictDifferentLength[letter] = 3

        horocyclic_edge_machine_1234 = fsm_generator.horocyclic_edge_checker(SubwordDict1234)
        horocyclic_edge_machine_1256 = fsm_generator.horocyclic_edge_checker(SubwordDict1256)
        horocyclic_edge_machine_different_length = fsm_generator.horocyclic_edge_checker(SubwordDictDifferentLength)
        
        assert(len(horocyclic_suffix_machine_1234.states) == 54)
        assert(len(horocyclic_suffix_machine_1234.transitions()) == 352)
        assert(len(horocyclic_suffix_machine_1256.states) == 45)
        assert(len(horocyclic_suffix_machine_1256.transitions()) == 298)
        assert(len(horocyclic_edge_machine_1234.states) == 322)
        assert(len(horocyclic_edge_machine_1234.transitions()) == 1122)
        assert(len(horocyclic_edge_machine_1256.states) == 272)
        assert(len(horocyclic_edge_machine_1256.transitions()) == 863)
        assert(len(horocyclic_edge_machine_different_length.states) == 272)
        assert(len(horocyclic_edge_machine_different_length.transitions()) == 863)

        #Case 2: for the weird group
        Data = WeirdGroupData()
        fsm_generator = Divergence_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        horocyclic_suffix_machine_1234 = fsm_generator.horocyclic_suffix_machine_1234()
        horocyclic_suffix_machine_1256 = fsm_generator.horocyclic_suffix_machine_1256()
        SubwordDict1234 = {}
        SubwordDict1256 = {}
        SubwordDictDifferentLength = {}
        for letter in Data.c_map[Data.ray[0]].intersection(fsm_generator.lesser_star[Data.ray[1]]):
            SubwordDict1234[letter] = 1
            SubwordDict1256[letter] = 1
            SubwordDictDifferentLength[letter] = 1
        for letter in fsm_generator.lesser_star[Data.ray[0]].intersection(fsm_generator.greater_star[Data.ray[1]]):
            SubwordDict1234[letter] = 2
            SubwordDict1256[letter] = 2
            SubwordDictDifferentLength[letter] = 2
        for letter in fsm_generator.lesser_star[Data.ray[1]].difference(Data.c_map[Data.ray[0]]):
            SubwordDict1234[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[1]].union(fsm_generator.lesser_star[Data.ray[0]].intersection(Data.c_map[Data.ray[1]]))):
            SubwordDict1234[letter] = 4
        for letter in fsm_generator.lesser_star[Data.ray[0]].difference(Data.c_map[Data.ray[1]]):
            SubwordDict1256[letter] = 3
        for letter in fsm_generator.alphabet.difference(fsm_generator.lesser_star[Data.ray[0]].union(fsm_generator.lesser_star[Data.ray[1]].intersection(Data.c_map[Data.ray[0]]))):
            SubwordDict1256[letter] = 4
        for letter in fsm_generator.alphabet:
            try:
                SubwordDictDifferentLength[letter]
            except KeyError:
                SubwordDictDifferentLength[letter] = 3

        horocyclic_edge_machine_1234 = fsm_generator.horocyclic_edge_checker(SubwordDict1234)
        horocyclic_edge_machine_1256 = fsm_generator.horocyclic_edge_checker(SubwordDict1256)
        horocyclic_edge_machine_different_length = fsm_generator.horocyclic_edge_checker(SubwordDictDifferentLength)
        
        assert(len(horocyclic_suffix_machine_1234.states) == 38)
        assert(len(horocyclic_suffix_machine_1234.transitions()) == 220)
        assert(len(horocyclic_suffix_machine_1256.states) == 21)
        assert(len(horocyclic_suffix_machine_1256.transitions()) == 129)
        assert(len(horocyclic_edge_machine_1234.states) == 323)
        assert(len(horocyclic_edge_machine_1234.transitions()) == 1137)
        assert(len(horocyclic_edge_machine_1256.states) == 168)
        assert(len(horocyclic_edge_machine_1256.transitions()) == 571)
        assert(len(horocyclic_edge_machine_different_length.states) == 168)
        assert(len(horocyclic_edge_machine_different_length.transitions()) == 571)

    def test_virtual_surface_divergence_graph(self):
        Data = VirtualSurfaceData()
        HorosphereGenerator = DivergenceHorosphereGenerator(Data.c_map, Data.o_map, Data.ray)
        Graph = HorosphereGenerator.horosphere_as_networkx(3, 0)
        self.assertEqual(Graph.number_of_edges, Graph.number_of_nodes - 1) 