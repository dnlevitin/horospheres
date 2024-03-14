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
from rips_fsm_generator import Rips_FSM_Generator

class RipsHorosphereGenerator:
    def __init__(self, commutation_dict: dict[str, set], order_dict: dict[str, int], ray: list[str]):
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray
        fsm_gen = Rips_FSM_Generator(self.c_map, self.o_map, self.ray)
        self.suffix_generator = fsm_gen.shortlex_suffix_machine
        self.geodesic_suffix_machine = fsm_gen.geodesic_suffix_machine
        self.ray_excluder = fsm_gen.__FSM_Generator_first_letter_excluder(set(ray))
        self.word_gen = WordGenerator(self.c_map, self.o_map)

    def get_all_length_n_suffixes(self, n:int) -> list:
        """
        Finds all suffixes of length at most n by a BFS.

        :param n: The depth with which the BFS will be conducted.
        :return: A list of all shortlex suffixes of length at most n, formatted as instances of the Word class.
        """
        
        n += 1
        origin = self.suffix_generator.initial_states()[0]

        # All elements of the frontier are of the form (FSMState, current depth, word)
        frontier = [(origin, 0, self.word_gen.word([]))]
        # We will add the words to words_out
        words_out = []

        while frontier:
            state, depth, word = frontier.pop(0)
            # Only go to depth n
            if depth == n:
                continue

            words_out.append(word)

            # Continue traversing
            for transition in self.suffix_generator.iter_transitions(state):
                frontier.append(transition.to_state, depth+1, self.word_gen.word(word.word_as_list + transition.word_in))

        return words_out

    def calculate_same_length_rips_adjacencies(self, suffix:Word) -> list:
        """
        Given a shortlex suffix, find all suffixes of the same length on the same horosphere that are at distance 2.

        :param suffix: A shortlex suffix.
        :return: The list of all suffixes of the same length as suffix that are at distance 2 from suffix.
        """

        SuffixMachineState = self.suffix_generator.process(suffix.word_as_list)
        
        if not SuffixMachineState[0]:
            raise ValueError('The input is not a shortlex suffix')
        
        # Edge case: empty string "". There are no other length-0 words 
        if len(suffix) == 0:
            return []

        GeodesicSuffixMachineState = self.geodesic_suffix_machine.process(suffix.word_as_list)[1]
        adjacencies = []
        
        for last_letter in GeodesicSuffixMachineState.label()[0]:

            # Remove the last instance of last_letter from the word.
            reversed_word = suffix.word_as_list[::-1]
            deleted_word = (reversed_word[0:reversed_word.index(last_letter):]+reversed_word[reversed_word.index(last_letter)+1::])[::-1]

            deleted_word_state = self.geodesic_suffix_machine.process(deleted_word.word_as_list)[1]

            #The valid letters are those that will not cancel, will not join the prefix, and are not last_letter itself
            connecting_letters = self.alphabet.difference(set(deleted_word_state.label()[0]).union(set(deleted_word_state.label()[1])).union({last_letter}))

            # Lengthen the reduced word by its geodesic legal next letters to get all same length adjacent suffixes
            for letter in connecting_letters:
                adjacencies.append(deleted_word.copy().shortlex_append(letter))

        return adjacencies

    def calculate_different_length_rips_adjacencies(self, suffix: Word, mode:int) -> list:
        """
        Given a suffix, this method finds all suffixes that are 1 letter shorter so that the related words are at distance 2.

        :param suffix: A shortlex suffix.
        :param mode: either 0 or 1. The prefix letter to be deleted or added is self.ray[mode].
        :return: The list of all such suffixes.
        """

        suffix_state = self.suffix_generator.process(suffix.word_as_list)[1]

        adjacencies = []

        #Edge case: suffixes of length 0.
        #There are no suffixes of negative length.
        if len(suffix) == 0:
            return adjacencies

        GeodesicSuffixMachineState = self.geodesic_suffix_machine.process(suffix.word_as_list)[1]

        for last_letter in GeodesicSuffixMachineState.label()[0]:

            # Remove the last instance of last_letter from the word.
            reversed_word = suffix.word_as_list[::-1]
            deleted_word = (reversed_word[0:reversed_word.index(last_letter):]+reversed_word[reversed_word.index(last_letter)+1::])[::-1]

            #Check whether to keep this word.
            if self.ray[mode] in set(self.ray_excluder.process(deleted_word.word_as_list)[1].label()):
                adjacencies.append(deleted_word)
                
        return adjacencies

    def calculate_rips_adjacencies(self, suffix:Word, BusemannValue: int) -> list:
        """
        Use "calculate_same_length_rips_adjacencies" and "calculate_different_length_rips_adj" to find all adjacent words which are at most as long as suffix.

        :param suffix: A shortlex suffix.
        :return: All adjacent suffixes at most as long as "suffix".
        """

        adjacencies = []

        mode = 1-((BusemannValue - len(suffix))%2)
        
        adjacencies.extend(self.calculate_same_length_rips_adjacencies(suffix))
        adjacencies.extend(self.calculate_different_length_rips_adjacencies(suffix, mode))
        return adjacencies

    def calculate_horosphere_edges(self, suffix_list: list, BusemannValue: int) -> list:
        """
        Calculate the set of edges from entries of suffix_list to shorter suffixes.

        :param suffix_list: A list of suffixes.
        :param BusemannValue: Value of the Busemann function for the horosphere.
        :return: A list of all pairs of suffixes whose corresponding words are at distance 2, 
        such that the first is an entry of suffix_list and the second is no longer than the first.
        """

        edges = []

        for suffix in suffix_list:
            edges.append( (str(suffix), str(newsuffix)) for newsuffix in self.calculate_rips_adjacencies(suffix, BusemannValue) )
        return(edges)
        
    def horosphere_as_networkx(self, length: int, BusemannValue: int):
        suffixes = self.get_all_length_n_suffixes(length)
        print(f"Suffixes of length {length} calculated: \n\t\t {len(suffixes)} words found")
        edges = self.calculate_horosphere_edges(suffixes, BusemannValue)
        print(f"Words processing completed: \n\t\t {len(suffixes)} words processed")

        G = nx.Graph()
        G.add_edges_from(edges)
        print(f"Length {length} Horosphere generated: \n\t\t {G}")
        return G