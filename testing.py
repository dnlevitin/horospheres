import unittest 
from rips_fsm_generator import Rips_FSM_Generator
from rips_horosphere_generator import RipsHorosphereGenerator
from divergence_horosphere_generator import DivergenceHorosphereGenerator
from defining_data import WeirdGroupData, SierpinskiCarpetData, VirtualSurfaceData
from sage.combinat.finite_state_machine import FSMTransition, Automaton

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """

    def test_geodesic_machine_list_input(self):
        Data = VirtualSurfaceData()
        fsm_generator = Rips_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine()
        #These assertions tell us that the machine has the expected number of states and transitions.
        assert(len(geodesic_machine.states()) == 11)
        assert(len(geodesic_machine.transitions()) == 40)
        #This assertion works fine
        assert(geodesic_machine.process( ['a'] )[0])
        #This assertion works fine
        transition_list = geodesic_machine.transitions(geodesic_machine.state(geodesic_machine.process( ['a'] )[1]))
        assert(any( transition.word_in [0] == 'c' for transition in transition_list ))
        #This assertion throws the error 'ValueError: State ('c',) does not belong to a finite state machine'
        assert(geodesic_machine.process( ['a', 'c'] )[0])

    def test_geodesic_machine_tuple_input(self):
        Data = VirtualSurfaceData()
        fsm_generator = Rips_FSM_Generator(Data.c_map, Data.o_map, Data.ray)
        geodesic_machine = fsm_generator._Rips_FSM_Generator__geodesic_machine()
        #These assertions tell us that the machine has the expected number of states and transitions.
        assert(len(geodesic_machine.states()) == 11)
        assert(len(geodesic_machine.transitions()) == 40)
        #This assertion works fine
        assert(geodesic_machine.process( tuple(('a')) )[0])
        #This assertion works fine
        transition_list = geodesic_machine.transitions(geodesic_machine.state(geodesic_machine.process( tuple(('a')) )[1]))
        assert(any( transition.word_in [0] == 'c' for transition in transition_list ))
        #This assertion throws the error 'ValueError: State ('c',) does not belong to a finite state machine'
        assert(geodesic_machine.process( ('a', 'c') )[0])

    def test_virtual_surface_divergence_graph_mockup(self):
        #I am getting a strange error in processing a specific stage in test_virtual_surface_divergence_graph.

        #This transition list mocks up part of the machine that appears in the above comment.
        TransitionList = [FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (4, 4), True), ('a', 'a')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (4, 4), True), ('e', 'e')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (4, 4), True), ('c', 'c')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ('b', 'b')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (4, 4), True), ('d', 'd')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('e',), ((('e',), ('a', 'd')),), ('a',), ('b', 'e'), (4, 4), True), ('a', 'e')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('a',), ((('a',), ('b', 'e')),), ('b',), ('a', 'c'), (4, 1), False), ('a', 'b')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('e',), ((('e',), ('a', 'd')),), ('a',), ('b', 'e'), (4, 4), False), ('e', 'a')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('e',), ((('e',), ('a', 'd')),), ('d',), ('c', 'e'), (4, 4), False), ('e', 'd')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('c',), ((('c',), ('b', 'd')),), ('b',), ('a', 'c'), (4, 1), False), ('c', 'b')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('d',), ((('d',), ('c', 'e')),), ('c',), ('b', 'd'), (4, 4), True), ('c', 'd')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('a',), ((('a',), ('b', 'e')),), ('b',), ('a', 'c'), (1, 4), True), ('b', 'a')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('c',), ((('c',), ('b', 'd')),), ('b',), ('a', 'c'), (1, 4), True), ('b', 'c')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('e',), ((('e',), ('a', 'd')),), ('d',), ('c', 'e'), (4, 4), True), ('d', 'e')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), ('d',), ((('d',), ('c', 'e')),), ('c',), ('b', 'd'), (4, 4), False), ('d', 'c')),
        FSMTransition(((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True), ((), (), (), (), (), (), (), (), (), ('a', 'b', 'c', 'd', 'e'), (4, 4), True, 'final'), ('-', '-'))]
        SuspectMachine = Automaton(TransitionList, initial_states = [((), (), (), (), (), (), (), (), (), ('a', 'e', 'c', 'b', 'd'), (1, 1), True)])

        #Check that there are no branches
        assert(SuspectMachine.is_deterministic())
        #Check that there are no epsilon transitions
        assert(transition.word_in[0] != None for transition in SuspectMachine.iter_transitions())
        #Check that there is a unique starting state.
        assert(len(SuspectMachine.initial_states()) == 1)
        #Check that each stage of the input can be processed.
        FirstTransitionIter = SuspectMachine.iter_transitions(SuspectMachine.initial_states()[0])
        FirstLabelList = [transition.word_in[0] for transition in FirstTransitionIter]
        assert(any(label == ('b' , 'b') for label in FirstLabelList))
        #The bug appears in the following line, which represents a step that occurs in processing the first input.
        #In this version, we get the ValueError State ((), (), (), (), (), (), (), (), (), ('a', 'b', 'd', 'e', 'c'), (1, 1), True) does not belong to a finite state machine while checking epsilon successors
        SecondState = SuspectMachine.process([('b', 'b')])[1]
        #In this version, we get the AttributeError 'FSMState' object has no attribute 'transitions'
        #SecondState = SuspectMachine.process([('b', 'b')], check_epsilon_transitions = False)[1]

        '''
        These lines do not run because of the above bug.
        SecondTransitionIter = SuspectMachine.iter_transitions(SecondState)
        SecondLabelList = [transition.word_in[0] for transition in SecondTransitionIter]
        assert(any(label == ('e', 'd') for label in SecondLabelList))
        ThirdState = SuspectMachine.process([('b', 'b'), ('e', 'd')])[1]
        ThirdTransitionIter = SuspectMachine.iter_transitions(ThirdState)
        ThirdLabelList = [transition.word_in[0] for transition in ThirdTransitionIter]
        assert(any(label == ('-', '-') for label in ThirdLabelList))
        #Check that the final state is accepted as is expected.
        assert(SuspectMachine.process( [('b', 'b'), ('e', 'd'), ('-', '-')])[0])
        '''
