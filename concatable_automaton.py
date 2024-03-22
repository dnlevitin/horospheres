from _collections_abc import Sequence, Iterable
from abc import ABC
from sage.combinat.finite_state_machine import FiniteStateMachine, FSMState, FSMTransition, Automaton
from sage.combinat.subset import powerset
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
import copy

class ConcatableAutomaton(Automaton):
    #This is the class for the automata we will use in this paper.

    def __init__(self, *args, **kwargs):
        """
        This is the initialization statement copied for automata
        """
        super().__init__(*args, **kwargs)
    
    def unambiguous_concatenation(self, other: 'ConcatableAutomaton') -> 'ConcatableAutomaton':
        '''
        A custom concatenation function for ConcatableAutomata M_1, M_2 with languages L_1 and L_2, satisfying the following:
        (1) M_1 and M_2 have no epsilon transitions
        (2) No word of L_1 ends with a letter that a word of L_2 begins with.
        (3) L_2 contains the empty word.
        The code is a modification of the .concatenation(other) method from sage.combinat.finite_state_machine.
        If (2) is not satisfied, this should output a non-deterministic automaton recognizing L_1L_2
    
        :param other: a non-empty Concatable Automaton.

        :return: a ConcatableAutomaton without epsilon transitions recognizing the concatenated language L_1L_2
        '''

        TransitionList = []
        first_states = {}
        second_states = {}
        for s in self.iter_states():
            new_state = s.relabeled((0, s.label()))
            first_states[s] = new_state
            #Unlike in sage.combinat.finite_state_machine, we allow these states to be final when the state they are copying is final. This means that each word w_1 in L_1 will again be accepted by the result, without needing an epsilon transition to a starting state of M_2

    
        for s in other.iter_states():
            new_state = s.relabeled((1, s.label()))
            new_state.is_initial = False
            second_states[s] = new_state

        for t in self.iter_transitions():
            NewTransition = FSMTransition(first_states[t.from_state],
                                          first_states[t.to_state],
                                          t.word_in,
                                          t.word_out)
            TransitionList.append(NewTransition)

        for t in other.iter_transitions():
            if (t.from_state).is_initial:
                continue
            NewTransition = FSMTransition(second_states[t.from_state],
                                          second_states[t.to_state],
                                          t.word_in,
                                          t.word_out)
            TransitionList.append(NewTransition)

        for s in self.iter_final_states():
            first_state = first_states[s]
            for t in other.iter_initial_states():
                second_state = second_states[t]
                #Unlike in sage.combinat.finite_state_machine, we create labeled transitions directly to those states in other that immediately follow initial states. This avoids the creation of epsilon transitions.
                for transition in other.transitions(t):
                    NewTransition = FSMTransition (first_state,
                                                   second_states[transition.to_state],
                                                   transition.word_in,
                                                   transition.word_out)
                    TransitionList.append(NewTransition)
   
        return ConcatableAutomaton(TransitionList)

    def concatable_intersection(self, other: 'ConcatableAutomaton', only_accessible_components = True) -> 'ConcatableAutomaton':
        #Compute self.intersection(other) as in sage.combinat.finite_state_machine, but return ConcatableAutomaton

        return ConcatableAutomaton(self.intersection(other, only_accessible_components))
    
    def _interspersal(self, other: 'ConcatableAutomaton') -> 'ConcatableAutomaton':
        '''Let the languages L_0 and L_1 be recognized respectively by self and other. This method takes the union of the even-length words in L_0 and the odd-length words in L_1
        
        :param self: A ConcatableAutomaton.
        :param other: A ConcatableAutomaton.

        :return: A ConcatableAutomaton recognizing the even-length words accepted by self and the odd length words accepted by other.     
        '''
        
        self.input_alphabet = set(self.input_alphabet).union(set(other.input_alphabet))
        other.input_alphabet = set(self.input_alphabet).union(set(other.input_alphabet))
        
        CompleteSelf = self.completion()
        CompleteOther = other.completion()
        
        #Define an automaton to keep track of the parity of the lengths of words.
        
        EvenState = FSMState(0, is_initial = True, is_final = True)
        OddState = FSMState(1, is_initial = False, is_final = True)
        TransitionList = []
        for letter in set(self.input_alphabet).union(set(other.input_alphabet)):
            TransitionList.append(FSMTransition(EvenState, OddState, letter))
            TransitionList.append(FSMTransition(OddState, EvenState, letter))
        ParityMachine = ConcatableAutomaton(TransitionList)
        
        ApproxMachine = ParityMachine.concatable_intersection(CompleteSelf.concatable_intersection(CompleteOther))
        #Because all these machines are complete, self.concatable_intersection(other) will still track its progress in other of a word rejected by self, and vice versa.
        #States (n, (self.state(spam), other.state(spam))) are final iff both (self.state(spam)) and (other.state(spam)) are, where n is either EvenState or OddState. So this automaton has the correct states but no final states.
        
        for state in ApproxMachine.iter_states():
            #Labels are of the form (n, (self.state(spam), other.state(spam))). We need n.label() to get the parity. 
            parity = (state.label()[0]).label()
            state.is_final = state.label()[1].label()[parity].is_final

        return ApproxMachine


    def next_letters(self, state: FSMState)->set:
        '''
        Generate the collection of letters that label the transitions exiting a particular state.
        Note that transitions that do not lead to final states are included, as are transitions to fail states (i.e. those from which it is impossible to reach a final state)

        :param state: an FSMState of self.
        :return: the set of letters that can be written after the given state.
        '''

        if not self.has_state(state):
            raise ValueError('The state', state.label(), 'is not in this machine.')

        #Recall that transition.word_in returns a singleton list
        return {transition.word_in[0] for transition in self.iter_transitions(state)}
"""
     
    def transition_dict(self, state:FSMState) -> dict:
        '''
        Generate a dictionary describing the FSMTransitions of self that start at the provided state.
        Keys to this dictionary are letters of the input alphabet, and values are instances of FSMtransition starting at state and labeled by the key value.
        
        :param state: a state in self.
        :return: A dictionary whose keys are the letters of the input alphabet and whose values are the transitions from state labeled by those keys.
        '''

        if not self.is_deterministic:
            raise ValueError('Not implemented for non-deterministic automata')
            
        TransitionDict = {}
        for transition in self.iter_transitions(state):
            TransitionDict[transition.word_in]=transition
        return TransitionDict

"""
