from _collections_abc import Sequence, Iterable
from abc import ABC
from sage.combinat.finite_state_machine import FiniteStateMachine, FSMState, FSMTransition, Automaton
from sage.combinat.subset import powerset
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
from words import Word, WordGenerator
import copy
from concatable_automaton import ConcatableAutomaton

class Rips_FSM_Generator:
    def __init__(self, commutation_dict:dict[str, set], order_dict: dict[str, int], ray: list[str]):
        
        '''
        This object will make the necessary automata for the Rips graph on a horosphere.
    
        :param commutation_dict: A dictionary representation of a defining graph. A letter (key) is associated with a list of letters (value) that the key letter commutes with. This list should not include the key letter.
        Note: this program does not check that commutation_dict is symmetrical. You need to make sure that if your input allows a_i to commute with a_j, then a_j is also allowed to commute with a_i.
        :param order_dict: A dictionary representation of a total ordering on the letter in the defining graph. A letter (key) is associated with an index (value) that represents that letters relative position in the ordering.
        :param ray: A list of two characters that will be used to generate the chosen ray to infinity. In the paper these are referred to as a_i and a_j respectively.
        '''

        if not len(ray) == 2:
            raise ValueError ("The defining ray should have two letters")
        elif ray [1] in commutation_dict[ray[0]]:
            raise ValueError ("The defining ray consists of two letters which commute")
        
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray

        StringOfAllLetters = ''.join(letter for letter in self.alphabet)
        if '-' in StringOfAllLetters:
            raise ValueError ('''The character '-' is reserved to be the blank character''')
        if ',' in StringOfAllLetters:
            raise ValueError('''The character ',' is reserved for delimiting lists''')
        if '_' in StringOfAllLetters:
            raise ValueError(''' The character '_' is reserved for the word breaks in horocyclic suffices''')
        
        #the lesser_star dictionary agrees with the function Star_< in the paper. When passed a key of a letter, it returns the set of letters that commute with and precede the key. Note the strict inequality.
        self.lesser_star = {}
        for letter in self.alphabet:
            LesserStarOfLetter = set(filter(lambda x: self.o_map[x] < self.o_map[letter], self.c_map[letter]))
            self.lesser_star[letter] = LesserStarOfLetter
        self.greater_star = {}
        for letter in self.alphabet:
            self.greater_star[letter] = self.c_map[letter].difference(self.lesser_star[letter])

    
    def __first_letter_excluder(self, excluded_letters:set) -> ConcatableAutomaton:
        '''
        Generate an FSM that prevents a chosen set of letters from reaching the beginning of the word without cancellation. The states in this machine represent which letters could still reach the beginning of the word.
        
        :param excluded_letters: A set of letters which that accepted words should not begin with.
                
        :return: An automaton that accepts words which, without cancellation, cannot be commuted to begin with a letter in excluded_letters
        '''
        if excluded_letters == self.alphabet:
            print("It appears that every letter has been excluded. Returning an automaton that accepts only the empty string")
            SingleState = FSMState('origin', is_initial = True, is_final = True)
            return ConcatableAutomaton({SingleState:[]})
        sorted_excluded_letters = sorted(excluded_letters, key = lambda x: self.o_map[x])
        TransitionList = []
        Frontier = []
        StartStateName = tuple(sorted_excluded_letters)
        # StartStateName = ",".join(str(letter) for letter in sorted(excluded_letters, key = lambda x: self.o_map[x]))
        StartState = FSMState(StartStateName, is_initial = True, is_final = True)
        for nextletter in self.alphabet.difference(excluded_letters):
            NextName = tuple(sorted(excluded_letters.intersection(self.c_map[nextletter]), key = lambda x: self.o_map[x]))
            NextState = FSMState(NextName, is_initial = (NextName == StartStateName), is_final = True)
            TransitionList.append(FSMTransition(StartState, NextState, nextletter))
            Frontier.append(NextState)
            
        #FinishedStates keeps track of which vertices we have already found all the edges for.
        
        FinishedStates = [StartState]
        while len(Frontier)>0:
            SourceState = Frontier.pop(0)
            if SourceState in FinishedStates:
                continue
        
            SourceSet = set(SourceState.label())
            FinishedStates.append(SourceState)
            for nextletter in self.alphabet.difference(SourceSet):
                NextName = tuple(sorted(SourceSet.intersection(self.c_map[nextletter]), key = lambda x: self.o_map[x]))
                NextState = FSMState(NextName, is_initial = (NextName == StartStateName), is_final = True)
                Frontier.append(NextState)
                TransitionList.append(FSMTransition(SourceState, NextState, nextletter))
       
        #print('TransitionList is')
        #print(TransitionList)
        return(ConcatableAutomaton(TransitionList))
        

    def odd_accepter_machine(self) -> ConcatableAutomaton:
        '''
        This machine will accept words of odd length. Since words will be passed as lists of elements of the alphabet, the len function could do this.
        However, the tools in sage.combinat.finite_state_machine don't easily facilitate combining FSMs with functions.

        :return: An automaton whose accepted language consists of (unreduced) words of odd length.
        '''

        EvenState = FSMState('even', is_initial = True, is_final = False)
        OddState = FSMState('odd', is_initial = False, is_final = True)
        TransitionList = []
        for letter in self.alphabet:
            TransitionList.append(FSMTransition(EvenState, OddState, letter))
            TransitionList.append(FSMTransition(OddState, EvenState, letter))
        return ConcatableAutomaton(TransitionList)

    def even_accepter_machine(self) -> ConcatableAutomaton:
        '''
        This machine will accept words of even length. Since words will be passed as lists of elements of the alphabet, the len function could do this.
        However, the tools in sage.combinat.finite_state_machine don't easily facilitate combining FSMs with functions.

        :return: An automaton whose accepted language consists of (unreduced) words of odd length.
        '''

        EvenState = FSMState('even', is_initial = True, is_final = True)
        OddState = FSMState('odd', is_initial = False, is_final = False)
        TransitionList = []
        for letter in self.alphabet:
            TransitionList.append(FSMTransition(EvenState, OddState, letter))
            TransitionList.append(FSMTransition(OddState, EvenState, letter))
        return ConcatableAutomaton(TransitionList)
        
    def __shortlex_machine(self, restricted_alphabet = None) -> ConcatableAutomaton:
        """
        Generate an FSM that prevents letters from being written that either cancel or should have already been written. 
        The states of this automaton represent the list of letters that a word cannot be followed by if it is to remain shortlex

        :param restricted_alphabet: if desired, pass a subset of self.alphabet to get the shortlex machine for the special subgroup defined by the vertices in restricted_alphabet. If this set is empty, an FSM recognizing the empty word is returned.
        
        :return: An automaton whose accepted language consists of shortlex words.
        """
        if restricted_alphabet is None:
            restricted_alphabet = self.alphabet
        if not restricted_alphabet.issubset(self.alphabet):
            raise ValueError("argument restricted_alphabet is not a subset of self.alphabet")
        if restricted_alphabet == set():
            print("You have requested the shortlex machine on an empty alphabet. Returning an automaton that accepts only the empty string")
            SingleState = FSMState('origin', is_initial = True, is_final = True)
            return ConcatableAutomaton({SingleState:[]})
        
        StartState = FSMState((), is_initial = True, is_final = True)
        TransitionList = []
        Frontier = []
        States = [StartState]

        # Initialize the frontier with the legal next letters for single letter words 
        for nextletter in restricted_alphabet:

            # Set destination as the set of legal next letters for each letter
            NextName = tuple(sorted((self.lesser_star[nextletter].intersection(restricted_alphabet)).union({nextletter}), key = lambda x: self.o_map[x]))
            NextState = FSMState(NextName, is_initial = False, is_final = True)
            TransitionList.append(FSMTransition(StartState, NextState, nextletter))
            
            Frontier.append(NextState)

        # Run BFS until we have finished the machine
        while len(Frontier) > 0:
            SourceState = Frontier.pop(0)

            # We have already considered source and all its outgoing edges, we can skip it
            if SourceState in States:
                continue
            States.append(SourceState)

            # Record outgoing edges (i.e. possible next letters) from SourceState. This is guaranteed to be unique by above if-statement
            SourceSet = set(SourceState.label())
            for nextletter in restricted_alphabet.difference(SourceSet):
                # This line computes the new set of forbidden letters
                NextSet = SourceSet.intersection(self.c_map[nextletter]).union(self.lesser_star[nextletter].intersection(restricted_alphabet)).union({nextletter})
                NextName = tuple(sorted(NextSet, key = lambda x: self.o_map[x]))
                #We can never return to the original state, so the next state is always final and never initial.
                NextState = FSMState(NextName, is_initial = False, is_final = True)
                                
                # Add NextState to our frontier to ensure all vertices are reached
                Frontier.append(NextState)
                TransitionList.append(FSMTransition (SourceState, NextState, nextletter))
               
        #print(f"ShortLex Machine on alphabet {restricted_alphabet} Completed: Graph with \n\t\t{len(States)} Vertices and \n\t\t{len(TransitionList)} Edges.")
        return (ConcatableAutomaton(TransitionList))
    
    def __geodesic_machine(self, restricted_alphabet = None)->ConcatableAutomaton:
        """
        Generate an FSM that prevents letters from being written that cancel . 
        The states of this automaton represent the list of letters that a word cannot be followed by if it is to remain geodesic

        :param restricted_alphabet: if desired, pass a subset of self.alphabet to get the geodesic machine for the special subgroup defined by the vertices in restricted_alphabet.
        
        :return: An automaton whose accepted language consists of geodesic words.
        """
        if restricted_alphabet is None:
            restricted_alphabet = self.alphabet
        if not restricted_alphabet.issubset(self.alphabet):
            raise ValueError("argument restricted_alphabet is not a subset of self.alphabet")
        if restricted_alphabet == set():
            print("You have requested the geodesic machine on an empty alphabet. Returning an automaton that accepts only the empty string")
            SingleState = FSMState('origin', is_initial = True, is_final = True)
            return ConcatableAutomaton({SingleState:[]})
        
        StartState = FSMState((), is_initial = True, is_final = True)
        TransitionList = []
        Frontier = []
        States = [StartState]

        # Initialize the frontier with the legal next letters for single letter words 
        for nextletter in restricted_alphabet:

            # Set destination as the set of legal next letters for each letter
            NextName = (nextletter)
            NextState = FSMState(NextName, is_initial = False, is_final = True)
            TransitionList.append(FSMTransition(StartState, NextState, nextletter))
            
            Frontier.append(NextState)

        # Run BFS until we have finished the machine
        while len(Frontier) > 0:
            SourceState = Frontier.pop(0)

            # We have already considered source and all its outgoing edges, we can skip it
            if SourceState in States:
                continue
            States.append(SourceState)

            # Record outgoing edges (i.e. possible next letters) from SourceState. This is guaranteed to be unique by above if-statement
            SourceSet = set(SourceState.label())
            for nextletter in restricted_alphabet.difference(SourceSet):
                # This line computes the new set of forbidden letters
                NextSet = SourceSet.intersection(self.c_map[nextletter]).union({nextletter})
                NextName = tuple(sorted(NextSet, key = lambda x: self.o_map[x]))
                #We can never return to the original state, so the next state is always final and never initial.
                NextState = FSMState(NextName, is_initial = False, is_final = True)
                                
                # Add NextState to our frontier to ensure all vertices are reached
                Frontier.append(NextState)
                TransitionList.append(FSMTransition (SourceState, NextState, nextletter))
               
        #print(f"Geodesic Machine on alphabet {restricted_alphabet} completed: Graph with \n\t\t{len(States)} Vertices and \n\t\t{len(TransitionList)} Edges.")
        return (ConcatableAutomaton(TransitionList))
    
    def shortlex_suffix_machine(self) -> ConcatableAutomaton:
        return self.__shortlex_machine().concatable_intersection(self.__first_letter_excluder(set(self.ray)))

    def geodesic_suffix_machine(self) -> ConcatableAutomaton:
        return self.__geodesic_machine().concatable_intersection(self.__first_letter_excluder(set(self.ray)))