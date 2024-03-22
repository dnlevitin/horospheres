from _collections_abc import Sequence, Iterable
from abc import ABC
from sage.combinat.finite_state_machine import FiniteStateMachine, FSMState, FSMTransition, Automaton
from sage.combinat.subset import powerset
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
import copy

class WordGenerator:
    def __init__(self, commutation_dict: dict[str: list], order_dict: dict[str: int]):
        self.c_map = commutation_dict
        self.o_map = order_dict

    def word(self, word):
        return Word(word, self.c_map, self.o_map)

    def horocyclic_word(self, subwordlist, mode):
        return HorocyclicWord(subwordlist, mode, self.c_map, self.o_map)


class Word(Sequence):
    def __init__(self, word, commutation_dict: dict[str: list], order_dict: dict[str: int]):
        if word is list:
            self.word_as_list = word
        elif isinstance(word, Iterable):
            self.word_as_list = list(word)
        else:
            raise TypeError("argument 'word' is not iterable")
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in order_dict)
        # super.__init__()

    def __getitem__(self, item):
        return self.word_as_list[item]

    def __len__(self):
        return len(self.word_as_list)

    def __str__(self):
        return ''.join(str(a) for a in self.word_as_list)

    def __eq__(self, other):
        if isinstance(other, Word):
            return self.word_as_list == other.word_as_list
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return('Word(' + str(self.word_as_list) +')')

    def word_as_tuple (self) -> tuple:
        return (tuple(self.word_as_list))
    
    def copy(self):
        copy_word_list = list(letter for letter in self.word_as_list)
        return Word(copy_word_list, self.c_map, self.o_map)

    def append(self, value: str) -> None:
        self.word_as_list.append(value)

    def shortlex_append(self, value: str):
        optimal_insert_idx = len(self.word_as_list)
        for i in reversed(range(len(self.word_as_list))):
            if value not in self.c_map[self.word_as_list[i]]:
                break
            if self.o_map[self.word_as_list[i]] > self.o_map[value]:
                optimal_insert_idx = i
        self.word_as_list.insert(optimal_insert_idx, value)
        return self

    def insert(self, index: int, value: str):
        self.word_as_list.insert(index, value)
        return self

    def __neighborhood(self, letter: str) -> set:
        return set(self.c_map[letter])

class HorocyclicWord(Sequence):
    def __init__(self, subword_list:list, mode:bool, commutation_dict: dict[str: list], order_dict: dict[str: int]):
        '''
        :param subwordlist: a list of 4 lists. Each inner list should be a list of strings.
        :param mode: True if the word is of form 1234, False if the word is of form 1256. Note that the class will not check that the word is of the desired form.
        '''
        if len(subword_list) != 4:
            raise ValueError ('Please specify exactly 4 (possibly empty) subwords')
        
        for subword in subword_list:
            if type(subword) != list:
                raise ValueError('subwords should be formatted as lists of strings.')

        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in order_dict)
        self.mode = mode
        
        self.SubwordList = subword_list 
        self.final_subword = 0
        for i in reversed(range (0, 4)):
            if subword_list[i] != []:
                self.final_subword = i
                break

        self.word_as_list = subword_list[0]+subword_list[1]+subword_list[2]+subword_list[3]
                
    def __getitem__(self, item):
        return self.SubwordList[item]

    def __len__(self):
        return len(self.word_as_list)

    def __str__(self):
        return ''.join(str(a) for a in self.word_as_list)

    def __eq__(self, other):
        if isinstance(other, HorocyclicWord):
            return self.SubwordList == other.SubwordList
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return('HorocyclicWord(' + str(self.SubwordList) +')')
    
    def copy(self):
        copy_subword_list = [list(letter for letter in self.SubwordList[0]), list(letter for letter in self.SubwordList[1]), list(letter for letter in self.SubwordList[2]), list(letter for letter in self.SubwordList[3])]
        return HorocyclicWord(copy_subword_list, self.mode, self.c_map, self.o_map)
    
    def append(self, letter: str, position: int) -> None:
        if self.final_subword > position:
            raise ValueError ('cannot append to subwords which have ended')
        self.SubwordList[position].append(letter)
        self.word_as_list.append(letter)
        self.final_subword = position