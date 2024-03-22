from _collections_abc import Sequence, Iterable
from abc import ABC
from sage.combinat.finite_state_machine import FiniteStateMachine, FSMState, FSMTransition, Automaton
from sage.combinat.subset import powerset
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
import copy
from concatable_automaton import ConcatableAutomaton
from rips_fsm_generator import Rips_FSM_Generator
from words import WordGenerator

class Divergence_FSM_Generator(Rips_FSM_Generator):
    def __init__(self, commutation_dict:dict[str, set], order_dict: dict[str, int], ray: tuple[str]):
        
        '''
        This object will make the necessary automata for computing the Divergence Graph. 
    
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

        self.WordGeneratorMachine = WordGenerator(self.c_map, self.o_map)
        
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

    def horocyclic_suffix_machine_1(self) -> ConcatableAutomaton:
        #The w_1 machine accepts words spelled in the letters that commute with both letters of the ray and precede the second one (a_j in the paper)
        w1_machine = self._Rips_FSM_Generator__shortlex_machine(self.c_map[self.ray[0]].intersection(self.lesser_star[self.ray[1]]))

        return (w1_machine)

    def horocyclic_suffix_machine_2(self) -> ConcatableAutomaton:
        #The w_2 machine accepts words spelled in the letters that commute with both letters of the ray, precede the first one (a_i in the paper), and follow the second one.
        w2_machine = self._Rips_FSM_Generator__shortlex_machine(self.lesser_star[self.ray[0]].intersection(self.greater_star[self.ray[1]]))

        return(w2_machine)

    
    def horocyclic_suffix_machine_1234(self) -> ConcatableAutomaton:
        '''
        Generate an FSM which accepts one of the two horocyclically shortlex word forms.

        :return: an Automaton whose accepted language is the set of words w_1w_2w_3w_4 as described in the paper.
        ''' 

        #w_3w_4 is a concattenation of shortlex words such that
        # 1. w_3 is spelled with letters commuting with and preceding a_j, and which do not commute with a_i
        # 2. w_4 cannot be made to begin with a_i, a_j, or a letter commuting with and preceding a_j
        # 3. w_3w_4, as a whole, cannot be rearranged to begin with a letter commuting with both letters and preceding a_i

        w3_machine = self._Rips_FSM_Generator__shortlex_machine(self.lesser_star[self.ray[1]]).concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder(self.c_map[self.ray[0]]))

        #This machine is so-named because its language is not exactly the words w_4, since in fact whether a word is allowed to be w_4 depends on w_3 by condition 3 above
        w4_machine_approx = self._Rips_FSM_Generator__shortlex_machine().concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder(self.lesser_star[self.ray[1]].union(set(self.ray))))
        #If there are bugs, it's because of this machine, but I believe this machine is correct.

        w1_machine = self.horocyclic_suffix_machine_1()
        w2_machine = self.horocyclic_suffix_machine_2()
        w12_machine = w1_machine.unambiguous_concatenation(w2_machine)
        
        w3w4_machine = (w3_machine.unambiguous_concatenation(w4_machine_approx)).concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder({self.ray[0]}.union(self.lesser_star[self.ray[0]].intersection(self.c_map[self.ray[1]]))))

        return w12_machine.unambiguous_concatenation(w3w4_machine)

    def horocyclic_suffix_machine_1256(self) -> ConcatableAutomaton:
  
        '''
        Generate an FSM which accepts one of the two horocyclically shortlex word forms.

        :return: an Automaton whose accepted language is the set of words w_1w_2w_5w_6 as described in the paper.
        ''' 

        #w_5w_6 is a concattenation of shortlex words such that
        # 1. w_5 is spelled with letters commuting with and preceding a_i, and which do not commute with a_j
        # 2. w_6 cannot be made to begin with a_i, a_j, or a letter commuting with and preceding a_i
        # 3. w_5w_6, as a whole, cannot be rearranged to begin with a letter commuting with both a_i and a_j and preceding a_j
        
        w5_machine = self._Rips_FSM_Generator__shortlex_machine(self.lesser_star[self.ray[0]]).concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder(self.c_map[self.ray[1]]))

        #This machine is so-named because its language is not exactly the words w_6, since in fact whether a word is allowed to be w_6 depends on w_5 by condition 3 above
        w6_machine_approx = self._Rips_FSM_Generator__shortlex_machine().concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder(self.lesser_star[self.ray[0]].union(set(self.ray))))
        #If there are bugs, it's because of this machine, but I believe this machine is correct.

        w1_machine = self.horocyclic_suffix_machine_1()
        w2_machine = self.horocyclic_suffix_machine_2()
        w12_machine = w1_machine.unambiguous_concatenation(w2_machine)
        
        w5w6_machine = (w5_machine.unambiguous_concatenation(w6_machine_approx)).concatable_intersection(self._Rips_FSM_Generator__first_letter_excluder({self.ray[1]}.union(self.lesser_star[self.ray[1]].intersection(self.c_map[self.ray[0]]))))

        return w12_machine.unambiguous_concatenation(w5w6_machine)

    #We will not use the even_horocyclic_suffix_machine or the odd_horocyclic_suffix_machine in practice.
    
    def even_horocyclic_suffix_machine(self) -> ConcatableAutomaton:

        return ((self.horocyclic_suffix_machine_1256())._interspersal(self.horocyclic_suffix_machine_1234()))

    def odd_horocyclic_suffix_machine(self) -> ConcatableAutomaton:

        return ((self.horocyclic_suffix_machine_1234())._interspersal(self.horocyclic_suffix_machine_1256()))

    def horocyclic_edge_checker(self, SubwordDict) -> Automaton:
        '''
        This machine will check whether there is a divergence graph edge between two horocyclic suffixes of the same length.
        The inputs will be pairs (WLetter,VLetter) or the pair ('-','-'). The latter denotes the end of the word.

        The subroutines generate_states_without_uncancelables, generate_first_noncanceling_transitions, get_nonterminal_transitions,
        and get_double_blank_transition will all be defined later.
        
        :param SubwordDict: A dictionary that keeps track of which letters first appear in which subword. It will have values 1-4 if the two words are of the same length and values 1-3 if the two are of different lengths.
        This is because in the case that w_suff is 1 letter shorter than v_suff, we will compare w_1w_2w_3self.ray[1]w_4- with v_1v_2 v_6-, or w_1w_2w_5 self.ray[0]w_6- with v_1v_2 v_4-.
        In the first case, letters of w_3self.ray[1]w_4 can cancel with those of v_6, while in the second case, letters of w_5self.ray[0]w_6 can cancel with those of v_4.
        
        :return: an Automaton which accepts as inputs pairs of letters, one from w and one from v, such that the words such that the lengths of each word are equal and there is no uncancelable pair
        '''

        
        

        NonFinalStates = []
        FinalStates = []
        TotalTransitions = []
        FinishedStates = []

        FinalSubword = max(SubwordDict.values())

        (StatesWithoutUncancelables, NewTransitions) = self.generate_states_without_uncancelables(SubwordDict)

        print('Completed the uncancelable states. There are ', len(StatesWithoutUncancelables), ' of them.')
        
        NonFinalStates.extend(StatesWithoutUncancelables)
        TotalTransitions.extend(NewTransitions)
        
        for StateWithoutUncancelables in StatesWithoutUncancelables:
            (NewStates, NewTransitions) = self.generate_first_noncanceling_transitions(StateWithoutUncancelables,SubwordDict)
            NonFinalStates.extend(NewStates)
            TotalTransitions.extend(NewTransitions)
            FinishedStates.append(StateWithoutUncancelables)

        print('Completed the first batch of transitions. There are ', len(TotalTransitions), 'transitions and ', len(set(NonFinalStates)), ' states in total')
        
        while len(NonFinalStates)>0:
            SourceState = NonFinalStates.pop(0)
            if SourceState in FinishedStates:
                continue

            (NewStates, NewTransitions) = self.get_nonterminal_transitions(SourceState, SubwordDict)
            NonFinalStates.extend(NewStates)
            TotalTransitions.extend(NewTransitions)
            FinishedStates.append(SourceState)

        print('Completed the nonterminal transitions. There are ', len(TotalTransitions), ' transitions and ', len(set(FinishedStates)), ' states in total')
        
        for SourceState in FinishedStates:
            try:
                (FinalState, FinalTransition) = self.get_double_blank_transition(SourceState, FinalSubword)
            except TypeError:
                continue
            FinalStates.append(FinalState)
            TotalTransitions.append(FinalTransition)

        print('completed the final transitions. There are ', len(TotalTransitions), 'transitions and ', len(set(FinalStates)), ' final states in total')
        
        return Automaton(TotalTransitions)

    def horocyclic_edge_checker_different_length(self) -> Automaton:
        '''
        This machine will check whether there is an uncancelable pair between two horocyclic suffixes of length differing by 1. The first input is w and the second is v.
        v_3 or v_5, depending on the form of v, is necessarily empty to have such an edge. However, this machine will not check this fact explicitly.
        The inputs will be pairs (WLetter, VLetter) or the pair ('-', '-'). The latter denotes the end of the word.
        
        The subroutines generate_states_without_uncancelables, generate_first_noncanceling_transitions, get_nonterminal_transitions,
        and get_single_blank_transition will all be defined later.
        
        :return: an Automaton which accepts pairs (w_1w_2w_3self.ray[1]w_4-, v_1v_2 v_6-) and (w_1w_2w_4 self.ray[0]w_6-, v_1v_2 v_4-) such that the lengths of each word are equal and there is no uncancelable pair
        '''

        #if not (mode == '1234' or mode == '1256'):
            #raise ValueError(''' The mode should be either '1234' or '1256' ''')

        #This dictionary keeps track of the necessary changes to the parameters n_v and n_w
        SubwordDict = {}
        #The letters that commute with and precede both ray letters appear first in w_1
        for letter in self.c_map[self.ray[0]].intersection(self.lesser_star[self.ray[1]]):
            SubwordDict[letter] = 1
        #The letters that commute with both ray letters and precede only the first appear first in w_2
        for letter in self.lesser_star[self.ray[0]].intersection(self.greater_star[self.ray[1]]):
            SubwordDict[letter] = 2
        #Every other letter appears in one of the last two subwords, and these are all lumped into a single case.
        for letter in self.alphabet:
            try:
                SubwordDict[letter]
            except KeyError:
                SubwordDict[letter] = 3

        NonFinalStates = []
        PreFinalStates = []
        FinalStates = []
        TotalTransitions = []
        FinishedStates = []

        #The beginning of this machine is the same as the previous one. All that needs to change is that we need to check that there are precisely two input pairs ('-', 'letter').
        #Because of these two blank characters at the end of the word w, there is no need for an input ('-', '-') to indicate that the word has ended.
        
        (StatesWithoutUncancelables, NewTransitions) = self.generate_states_without_uncancelables(SubwordDict)

        print('Completed the uncancelable states. There are ', len(StatesWithoutUncancelables), ' of them.')
        
        NonFinalStates.extend(StatesWithoutUncancelables)
        TotalTransitions.extend(NewTransitions)
        
        for StateWithoutUncancelables in StatesWithoutUncancelables:
            (NewStates, NewTransitions) = self.generate_first_noncanceling_transitions(StateWithoutUncancelables,SubwordDict)
            NonFinalStates.extend(NewStates)
            TotalTransitions.extend(NewTransitions)
            FinishedStates.append(StateWithoutUncancelables)

        print('Completed the first batch of transitions. There are ', len(TotalTransitions), 'transitions and ', len(NonFinalStates), ' states in total')
        
        while len(NonFinalStates) > 0:
            SourceState = NonFinalStates.pop(0)
            if SourceState in FinishedStates:
                continue

            (NewStates, NewTransitions) = self.get_nonterminal_transitions(SourceState, SubwordDict)
            NonFinalStates.extend(NewStates)
            TotalTransitions.extend(NewTransitions)
            FinishedStates.append(SourceState)

        print('Completed the nonterminal transitions. There are ', len(TotalTransitions), ' transitions and ', len(set(FinishedStates)), ' states in total')
        
        for SourceState in set(FinishedStates):
            for letter in SourceState.label()[9]:
                holder = self.get_single_blank_transition(SourceState, letter, SubwordDict)
                if holder is None:
                    continue
                (PreFinalState, PreFinalTransition) = holder
                PreFinalStates.append(PreFinalState)
                TotalTransitions.append(PreFinalTransition)

        print('Completed the first set of blank transitions. There are ', len(TotalTransitions), 'transitions and ', len(set(PreFinalStates)), ' pre-final states in total')

        for SourceState in set(PreFinalStates):
            for letter in SourceState.label()[9]:
                holder = self.get_single_blank_transition(SourceState, letter, SubwordDict)
                if holder is None:
                    continue
                (FinalState, FinalTransition) = holder
                FinalStates.append(FinalState)
                TotalTransitions.append(FinalTransition)

        print('Completed the second set of blank transitions. There are ', len(TotalTransitions), 'transitions and ', len(set(FinalStates)), ' final states in total')
        
        return Automaton(TotalTransitions)
        
    '''
    What follow are subroutines for the methods horocyclic_edge_checker_same_length and horocyclic_edge_checker_different_length.
    To improve performance and make certain features of sage.combinat.finite_state_machine usable, the state labels must be hashable, but to make changes, we will want mutable types.

    The following describes the state labels
    4 entries for the subwords u_j (j=1, 2, 3, 4) of potentially cancelable letters. These will be tuples (hashable) or instances of the Word Class (mutable)
    4 entries for the geodesic first letters of each of the u_j, and of each of their truncations. These will be tuples of pairs of tuples (hashable) or lists of pairs of sets (mutable)
    This will be formatted as a tuple or list of pairs (first letters, potential first letters).
    These first 8 entries will alternate, so that the data for the subword u_j appears at indices 2*j-2 and 2*j-1.
    1 entry for the uncancelable letters, in a tuple (hashable) or set (mutable).
    1 entry for the letters that commute with each uncancelable letter, in a tuple (hashable) or set (mutable)
    1 tuple of 2 integers n_w and n_v keeping track of which subword the two inputs are on.
    1 bit. True will mean that the second input (v) is the one which contains the potentially cancelable letters. False will mean that the first input (w) contains the potentially cancelable letters. Its initial value is arbitrarily set to True.
    The two inputs are the 'adding input' (the word that has the cancelable letters) and the 'canceling input'. So the bit True means that v is adding and w is canceling

    All of the above data will be placed into a tuple (hashable) or list (mutable)
    '''
    
    def generate_states_without_uncancelables(self, SubwordDict:dict[str: int]) -> tuple:
        #There are at most 4 states without uncancelable letters. This method generates them and the transitions between them.
        #:param SubwordDict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
        #:return: A pair consisting of a list of states without uncancelable letters, and a list of the transitions between them.
        
        TransitionList = []
        StatesWithoutUncancelables = []

        #This state will always exist
        InitialState = FSMState( ( (), (), (),  (), (), (), (), (), (), tuple(self.alphabet), (1, 1), True ),
                              is_initial = True, is_final = False)

        StatesWithoutUncancelables.append(InitialState)

        #We only need a state without uncancelables for each subword that will actually appear.
        for value in set(SubwordDict.values()).difference({1}):
            NewState = FSMState( ( (), (), (),  (), (), (), (), (), (), tuple(self.alphabet), (value, value), True ) )
            StatesWithoutUncancelables.append(NewState)
               
        for SourceState in StatesWithoutUncancelables:
            for letter in self.alphabet:
                NewSubword = max(SourceState.label()[10][0], SubwordDict[letter])
                NewState = FSMState( ( (), (), (),  (), (), (), (), (), (), tuple(self.alphabet), (NewSubword, NewSubword), True ) ,
                              is_initial = (NewSubword == 1), is_final = False)
                TransitionList.append(FSMTransition(SourceState, NewState, (letter, letter)))

        return (StatesWithoutUncancelables, TransitionList)

    def generate_first_noncanceling_transitions(self, StateWithoutUncancelables:FSMState, SubwordDict:dict[str: int]) -> tuple:
        #This method generates all the remaining transitions out of the 4 states without uncancelables
        #:param StateWithoutUncancelables: An FSMState that is in the output state list of FSM_Generator.generate_states_without_uncancelables.
        #:param SubwordDict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
        #:return: A pair consisting of a list of the states that follow StateWithoutUncancelables and a list a of the transitions out of StateWithoutUncancelables.

        if StateWithoutUncancelables.label()[8] != ():
            raise ValueError('This state has uncancelable letters')
        
        ResultingStates = []
        Transitions = []
        
        for LetterPair in product(self.alphabet, self.alphabet):
            WLetter = LetterPair [0]
            VLetter = LetterPair [1]
            #We can assume the two commute, or else we immediately reach a failure state
            if WLetter not in self.c_map[VLetter]:
                #This includes the case that WLetter == VLetter
                continue

            #In this setting, we will need to change the value at every 
            NewLabel = self._mutable_label(StateWithoutUncancelables.label())
            NewNW = max(NewLabel[10][0], SubwordDict[WLetter])                    
            NewNV = max(NewLabel[10][1], SubwordDict[VLetter])
            NewLabel[10] = (NewNW, NewNV)
            #We compute the next value of the bit. True means that the v is the adding word and False means that w is the adding word.
            NewBit = ((NewNW < NewNV) or (NewNW == NewNV and self.o_map[WLetter] < self.o_map[VLetter]))
            NewLabel[11] = NewBit
            AddingLetter = LetterPair[int(NewBit)]
            AddingSubword = NewLabel[10][int(NewBit)]
            CancelingLetter = LetterPair[1-int(NewBit)]
            
            #Add the AddingLetter
            NewLabel[2*AddingSubword -2].append(AddingLetter)
            #The AddingLetter is the first letter of the relevant word. The other possible first letters are those that commute with it.
            NewLabel[2*AddingSubword -1].append( ({AddingLetter}, self.c_map[AddingLetter]) )
            
            #Since the Adding and Canceling letters do not equate, there is no need to check for cancelation. The CancelingLetter automatically becomes uncancelable.
            NewLabel[8] = {CancelingLetter}
            NewLabel[9].intersection_update(self.c_map[CancelingLetter])
            
            NewState = FSMState(self._hashable_label(NewLabel))
            ResultingStates.append(NewState)
            NewTransition = FSMTransition(StateWithoutUncancelables, NewState, LetterPair)
            Transitions.append(NewTransition)
        return(ResultingStates, Transitions)

    def get_nonterminal_transitions(self, SourceState:FSMState, SubwordDict: dict[str: int]) -> tuple:
        #This method generates all the nonterminal successors of a state that has some uncancelable letters
        #:param SourceState: An FSMState with some uncancelable letters. 
        #:param SubwordDict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
        #:return: A pair consisting of a list of the states that follow SourceState and a list a of the transitions out of SourceState.

        OldBit = SourceState.label()[11]
        (OldNW, OldNV) = SourceState.label()[10]
        OldSubwordPair = (OldNW, OldNV)

        ResultingStates = []
        Transitions = []

        for LetterPair in product(SourceState.label()[9], SourceState.label()[9]):
            WLetter = LetterPair [0]
            VLetter = LetterPair [1]
            AddingLetter = LetterPair[int(OldBit)]
            CancelingLetter = LetterPair[1-int(OldBit)]
            
            NewLabel = self._mutable_label(SourceState.label())
            NewNW = max(NewLabel[10][0], SubwordDict[WLetter])                    
            NewNV = max(NewLabel[10][1], SubwordDict[VLetter])
            NewSubwordPair = (NewNW, NewNV)
            AddingSubword = NewSubwordPair[int(OldBit)]
            CancelingSubword = NewSubwordPair[1-int(OldBit)]
            NewLabel[10] = NewSubwordPair

            #Append the new letter to the relevant subword
            NewLabel[2*AddingSubword-2].append(AddingLetter)
            #Update the first leters
            for FirstLettersSet in NewLabel[2*AddingSubword-1]:
                if AddingLetter in FirstLettersSet[1]:
                    FirstLettersSet[0].add(AddingLetter)
                FirstLettersSet[1].intersection_update(self.c_map[AddingLetter])
            NewLabel[2*AddingSubword-1].append( ({AddingLetter},self.c_map[AddingLetter]) )

            #Compute the next bit value
            PresentLetterList = NewLabel[0].word_as_list + NewLabel[2].word_as_list + NewLabel[4].word_as_list + NewLabel[6].word_as_list
            PresentLetterSet = set(PresentLetterList)
            #Check whether the bit value needs to be flipped
            LettersFollowingAllPresentLetters = copy.copy(self.alphabet)
            for letter in PresentLetterSet:
                LettersFollowingAllPresentLetters.intersection_update(self.greater_star[letter])
            BitFlip = ( (CancelingSubword > AddingSubword) or \
                       (CancelingSubword == AddingSubword) and CancelingLetter in LettersFollowingAllPresentLetters \
                      )
            #exor True is the same as not, while exor False does nothing.
            NewLabel[11] = OldBit ^ BitFlip

            if BitFlip:
                #Every previously cancelable letter will become uncancelable. 
                #This will create an uncancelable pair if any of them fail to cancel with one another or with the CancelingLetter.
                #We also check whether there are any duplicates among the PresentLetters.
                #It is not possible for the CancelingLetter to be in PresentLetters in this case, so we need not check for disjointness.
                if (len(PresentLetterList) > len(PresentLetterSet)) or (not (self._test_set_commutation(PresentLetterSet) and self._test_set_pair_commutation({CancelingLetter},PresentLetterSet))):
                    continue
                                
                #Add every remaining cancelable letter into the uncancelable set
                NewLabel[8] = NewLabel[8].union(PresentLetterSet)
                for letter in PresentLetterSet:
                    NewLabel[9].intersection_update(self.c_map[letter])
            
                #Delete every previously cancelable letter, and initialize a new single cancelable letter.
                #Because we have just flipped the bit, the NewCancelingSubword and CancelingLetter take the place that the NewAddingSubword and AddingLetter had
                
                for i in range(0,4):
                    NewLabel[2*i] = self.WordGeneratorMachine.word([])
                    NewLabel[2*i+1] = []
                NewLabel[2*CancelingSubword-2] = self.WordGeneratorMachine.word(CancelingLetter)
                NewLabel[2*CancelingSubword-1].append( ({CancelingLetter}, self.c_map[CancelingLetter]) )
                NewState = FSMState(self._hashable_label(NewLabel))
                ResultingStates.append(NewState)
                NewTransition = FSMTransition(SourceState, NewState, LetterPair)
                Transitions.append(NewTransition)
                continue

            #Since the bit has not flipped, we just need to process the canceling letter.
            NewLabel = self.process_canceling_letter(NewLabel, CancelingLetter, SubwordDict)
            if NewLabel is None:
                continue
            NewState = FSMState(self._hashable_label(NewLabel))
            ResultingStates.append(NewState)
            NewTransition = FSMTransition(SourceState, NewState, (WLetter, VLetter))
            Transitions.append(NewTransition)

        return (ResultingStates, Transitions)

    def process_canceling_letter(self, Label:list, CancelingLetter:str, SubwordDict:dict[str: int])-> list:
        #This method takes a mutable label of an FSMState to which the AddingLetter has already been added and for which the bit has not flipped, and evaluates whether the CancelingLetter cancels
        #This method updates the label to change the cancelable letters, uncancelable set, and list of accepted next letters appropriately.
        #:param Label: the mutable label of an FSMState.
        #:param CancelingLetter: the letter whose cancelation is to be tested.
        #:param SubwordDict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
        #:return: The mutable label of the resulting state, or None if processing CancelingLetter creates an uncancelable pair.

        CancelingSubword = Label[10][1-int(Label[11])]
        NewUncancelableList = []
        #If a new subword has started, then the remaining letters from the previous subword(s) become uncancellable
        for i in range (0, CancelingSubword-1):
            NewUncancelableList.extend(Label[2*i].word_as_list)
            Label[2*i] = self.WordGeneratorMachine.word([])
            Label[2*i+1] = []
        NewUncancelables = set(NewUncancelableList)
        #This will create an uncancellable pair if any of the newly uncancelable letters fail to commute with one another, or any of them fail to commute with a remaining letter, or if they don't commute with the CancelingLetter
        #Since there may be more NewUncancelables after checking whether the CancelingLetter cancels all we must check now is whether the CancelingLetter commutes to the matching AddingSubword 
        #It is not possible for CancelingLetter to be in NewUncancelables because because then CancelingLetter would have to have appeared in the adding subword earlier than possible. So there is not need to ask for disjointness
        if not self._test_set_pair_commutation({CancelingLetter}, NewUncancelables):
            return (None)

        #Now we check whether the CancelingLetter actually cancels.
        #This idiom avoids problems with indexing into empty lists.
        if CancelingLetter in next(iter(Label[2*CancelingSubword-1]), (set(), set()))[0]:
            CancelingIndex = Label[2*CancelingSubword-2].index(CancelingLetter)
            #These letters have just become uncancellable.
            NewUncancelableList.extend(Label[2*CancelingSubword-2][:CancelingIndex])
            #This is the remaining potentially cancelable word.
            Label[2*CancelingSubword-2] = self.WordGeneratorMachine.word(Label[2*CancelingSubword-2][CancelingIndex+1:])
            Label[2*CancelingSubword-1] = Label[2*CancelingSubword-1][CancelingIndex+1:]
            #Update which letters are present
            RemainingLetters = set(Label[0].word_as_list).union(set(Label[2].word_as_list),set(Label[4].word_as_list),set(Label[6].word_as_list))
            #Check whether there are duplicate uncancellable letters
            NewUncancelables = set(NewUncancelableList)
            if len(NewUncancelableList) > len(NewUncancelables):
                return(None)
            #Check whether there is an uncancellable pair, either between the new uncancelables or with the remaining letters. In this case we will demand disjointness.
            if not (self._test_set_pair_commutation(NewUncancelables , RemainingLetters, AllDistinct = True) and self._test_set_commutation(NewUncancelables)):
                return(None)
            #If there are no uncancelable pairs, then we get a new transition. We will update the uncancelable set and the set of accepted next letters outside the if statement.
            for letter in NewUncancelables:
                Label[8].add(letter)
                Label[9].intersection_update(self.c_map[letter])
            return(Label)
        else:
            #If the CancelingLetter does not cancel, then it joins the uncancelable set. We check whether this creates an uncancelable pair.
            NewUncancelables.add(CancelingLetter)
            RemainingLetters = set(Label[0].word_as_list).union(set(Label[2].word_as_list),set(Label[4].word_as_list),set(Label[6].word_as_list))
            if not (self._test_set_pair_commutation(NewUncancelables, RemainingLetters, True) and self._test_set_commutation(NewUncancelables)):
                return(None)
            #If there are no uncancelable pairs, then we get a new transition.
            for letter in NewUncancelables:
                Label[8].add(letter)
                Label[9].intersection_update(self.c_map[letter])
            return(Label)
    
    def get_double_blank_transition(self, SourceState:FSMState, FinalSubword:int)->tuple:
        #This method takes any nonterminal SourceState and computes the outgoing transition labeled ('-', '-').
        #:param SourceState: a non-final FSMState.
        #:param FinalSubword: 3 or 4, depending on the number of different values of SubwordDict.
        #:return: A pair consisting of a final state and a transition from SourceState to this final state labeled is ('-', '-'), or None if ending the inputs here yields an uncancelable pair.

        if SourceState.is_final:
            raise ValueError('The provided state is final already')
        NewLabel = self._mutable_label(SourceState.label())
        NewUncancelableList = []
        for i in range (1, FinalSubword):
            NewUncancelableList.extend(NewLabel[2*i-2].word_as_list)
            NewLabel[2*i-2] = self.WordGeneratorMachine.word([])
            NewLabel[2*i-1] = []
        PresentLetters = set(NewLabel[2*FinalSubword - 2].word_as_list)
        NewUncancelables = set(NewUncancelableList)
        #Checking whether there are duplicate uncancelable letters.
        if len(NewUncancelableList) > len(NewUncancelables):
            return(None)
        if not (self._test_set_commutation(NewUncancelables) and self._test_set_pair_commutation(NewUncancelables, PresentLetters, True)):
            return(None)
        for letter in NewUncancelables:
            NewLabel[8].add(letter)
            NewLabel[9].intersection_update(self.c_map[letter])
        NewLabel[10] = (FinalSubword, FinalSubword)
        
        NewLabel.append('final')
        #Necessary to prevent issues with states that have matching labels.
        
        NewState = FSMState(self._hashable_label(NewLabel), is_initial = False, is_final = True)
        return( NewState, FSMTransition (SourceState, NewState, ('-','-')) )

    '''
    For the case where the words are different length, we will need one more subroutine. Since the words are of different lengths, we will assume the first input w is the shorter word.
    Then we will pad the input so that w ends with 2 blank characters '-' so that w-- and v_1v_2v_3 self.ray[1] v_4 (or v_1v_2v_5 self.ray[0] v_6) are the same length
    Therefore, we give a subroutine to process input pairs ('-', letter).
    '''

    def get_single_blank_transition(self, SourceState: FSMState, InputLetter: str, SubwordDict: dict[str:int]) -> tuple:
        '''
        This method takes a SourceState and returns the result of a transition labeled ('-', 'InputLetter').
    
        :param SourceState: an instance of FSMState of the above form.
        :param InputLetter: The input letter of the subword v. This may be canceling or adding.
        :param SubwordDict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
    
        :return: a pair (NewState, NewTransition) if the input ('-', InputLetter) does not create an uncancelable pair. 
        NewTransition is an instance of FSMTransition whose from_state is SourceState and whose to_state is NewState.
        If an uncancelable pair is created, this method returns None.
        '''
        
        NewLabel = self._mutable_label(SourceState.label())
        NewUncancelableList = []
    
    
        #Subwords w_1 and w_2 have ended.
        NewNV = max(NewLabel[10][1], SubwordDict[InputLetter])
        NewLabel[10] = (3, NewNV)
        
        #We will process this input in two cases depending on whether InputLetter is adding or cancelling. The adding case is easiest.
    
        if NewLabel[11]:
            NewLabel[2*NewNV-2].append(InputLetter)
            for FirstLettersSet in NewLabel[2*NewNV-1]:
                if InputLetter in FirstLettersSet[1]:
                    FirstLettersSet[0].add(InputLetter)
                FirstLettersSet[1].intersection_update(self.c_map[InputLetter])
            NewLabel[2*NewNV-1].append( ({InputLetter},self.c_map[InputLetter]) )
            
        #We get a  bit flip in this case if NV < 3. 
            if NewNV < 3:
                NewLabel[11] = False
                PresentLetterList = NewLabel[0].word_as_list + NewLabel[2].word_as_list + NewLabel[4].word_as_list
                PresentLetterSet = set(PresentLetterList)
                #Every previously cancelable letter will become uncancelable. 
                #This will create an uncancelable pair if any of them fail to cancel with one another or with the CancelingLetter.
                #We also check whether there are any duplicates among the PresentLetters.
                if len(PresentLetterList)>len(PresentLetterSet) or ( not self._test_set_commutation(PresentLetterSet)):
                    return(None)
                
                #Add every remaining cancelable letter into the uncancelable set
                NewLabel[8]=NewLabel[8].union(PresentLetterSet)
                for letter in PresentLetterSet:
                    NewLabel[9].intersection_update(self.c_map[letter])
            
                #Delete every previously cancelable letter, which appear only in v_1 and v_2
                for i in range(0,3):
                    NewLabel[2*i] = self.WordGeneratorMachine.word([])
                    NewLabel[2*i+1] = []
                #The 12th entry of NewState.label() will count the number of ending transitions that have elapsed.
                try:
                    NewLabel[12] += 1
                except IndexError:
                    NewLabel.append(1)
                NewState = FSMState(self._hashable_label(NewLabel), is_final = (NewLabel[12] == 2))
                NewTransition = FSMTransition(SourceState, NewState, ('-', InputLetter))
                
                
                return(NewState, NewTransition)
    
            #if the bit has not flipped, there is nothing left to do.
            try:
                NewLabel[12] += 1
            except IndexError:
                NewLabel.append(1)
            NewState = FSMState(self._hashable_label(NewLabel), is_final = (NewLabel[12] == 2))
            NewTransition = FSMTransition(SourceState, NewState, ('-', InputLetter))
            return (NewState, NewTransition)

        #If the InputLetter is canceling, then the increase of NV may have created new uncancelable letters.
        NewUncancelableList = []
        for i in range (0, NewNV-1):
            NewUncancelableList.extend(NewLabel[2*i].word_as_list)
            NewLabel[2*i] = self.WordGeneratorMachine.word([])
            NewLabel[2*i+1] = []

        NewUncancelableSet = set(NewUncancelableList)
        RemainingLetterList = NewLabel[0].word_as_list + NewLabel[2].word_as_list + NewLabel[4].word_as_list
        RemainingLetterSet = set(RemainingLetterList)

        #Check if this creates an uncancelable pair.

        if (len(NewUncancelableList) > len(NewUncancelableSet)) or ( not self._test_set_commutation(NewUncancelableSet)) or ( not self._test_set_pair_commutation (NewUncancelableSet, RemainingLetterSet, True) ):
            return(None)

        #If there is no uncancelable pair, it is also possible to create a bit flip. It is not possible for n_v to be greater than 3, and the InputLetter is a letter of v.
        #Therefore, we only check if the InputLetter commutes with and follows every RemainingLetter.
        
        LettersFollowingAllRemainingLetters = copy.copy(self.alphabet)
        for letter in RemainingLetterSet:
            LettersFollowingAllRemainingLetters.intersection_update(self.greater_star[letter])
        
        if InputLetter in LettersFollowingAllRemainingLetters:
            #Every RemainingLetter will become uncancelable. Check whether this creates an uncancelable pair.
            if (len(RemainingLetterList) > len(RemainingLetterSet) or not self._test_set_commutation(RemainingLetterSet)):
                return(None)
            
            NewLabel[8] = NewLabel[8].union(RemainingLetterSet)
            for letter in RemainingLetterSet:
                    NewLabel[9].intersection_update(self.c_map[letter])
            for i in range(0,4):
                NewLabel[2*i] = self.WordGeneratorMachine.word([])
                NewLabel[2*i+1] = []
                
            #the InputLetter becomes the only cancelable letter if it is in subword 3. Otherwise it becomes uncancelable as well.
            
            if NewNV == 3:
                NewLabel[4] = self.WordGeneratorMachine.word([InputLetter])
                NewLabel[5].append(({InputLetter}, self.c_map[InputLetter]))
                NewLabel[11] = True

                try:
                    NewLabel[12] += 1
                except IndexError:
                    NewLabel.append(1)
                NewState = FSMState(self._hashable_label(NewLabel), is_final = (NewLabel[12] == 2))
                NewTransition = FSMTransition(SourceState, NewState, ('-',InputLetter))
                return (NewState, NewTransition)

            #The InputLetter becomes uncancellable. We know already that it commutes with every other letter.
            NewLabel[8].add(InputLetter)
            NewLabel[9].intersection_update(self.c_map[InputLetter])
            try:
                NewLabel[12] += 1
            except IndexError:
                NewLabel.append(1)
            NewState = FSMState(self._hashable_label(NewLabel), is_final = (NewLabel[12] == 2))
            NewTransition = FSMTransition(SourceState, NewState, ('-',InputLetter))
            return (NewState, NewTransition)

        #If the bit has not flipped, then we process the InputLetter as a canceling letter.
        NewLabel = self.process_canceling_letter(NewLabel, InputLetter, SubwordDict)
        if NewLabel is None:
            return (None)
        try:
            NewLabel[12] += 1
        except IndexError:
            NewLabel.append(1)
        NewState = FSMState(self._hashable_label(NewLabel), is_final = (NewLabel[12] == 2))
        NewTransition = FSMTransition(SourceState, NewState, ('-',InputLetter))
        return (NewState, NewTransition)

    def _mutable_label(self, HashableLabel:tuple) -> list:
        '''
        This method takes a hashable label, as described above, and renders it mutable.
        '''
    
        MutableLabel = list(HashableLabel)
        
        for i in range (0, 4):
            MutableLabel[2*i] = self.WordGeneratorMachine.word(HashableLabel[2*i])
            NewList = []
            for (FirstLetterTuple, PotentialFirstLetterTuple) in HashableLabel[2*i+1]:
                NewList.append( (set(FirstLetterTuple), set(PotentialFirstLetterTuple)) )
            MutableLabel[2*i+1] = NewList
        MutableLabel[8] = set(HashableLabel[8])
        MutableLabel[9] = set(HashableLabel[9])
        
        return(MutableLabel)
    
    def _hashable_label(self, MutableLabel:list) -> tuple:
        '''
        This method takes a mutable state label as described above, and renders it hashable.
        '''
        for i in range (0, 4):
            MutableLabel[2*i] = MutableLabel[2*i].word_as_tuple()
            NewList = []
            #Coerce the first letter data into tuples 
            for (FirstLetterSet, PotentialFirstLetterSet) in MutableLabel[2*i+1]:
                NewList.append( ( tuple(sorted(FirstLetterSet, key = lambda x: self.o_map[x])), tuple(sorted(PotentialFirstLetterSet, key = lambda x: self.o_map[x])) ) )
            MutableLabel[2*i+1]=tuple(NewList)
        if isinstance(MutableLabel[8], set):
            MutableLabel[8] = tuple(sorted(MutableLabel[8], key = lambda x: self.o_map[x]))
        if isinstance(MutableLabel[9], set):
            MutableLabel[9] = tuple(sorted(MutableLabel[9], key = lambda x: self.o_map[x]))
    
        return(tuple(MutableLabel))

    def _test_set_commutation(self, LetterSet: set) -> bool:
        #This method takes as input a set of characters in self.alphabet and checks whether they pairwise commute.
        LetterList = sorted(LetterSet, key = lambda x: self.o_map[x])
        for i in range(0, len(LetterList)):
            #There is no need to include LetterList[i] in the set of letters it commutes with, because LetterSet is a set. We will never test its commutation against itself.
            IthLetterNeighbors = self.c_map[LetterList[i]]
            for j in range(i+1, len(LetterList)):
                if j not in IthLetterNeighbors:
                    return(False)
        return(True)

    def _test_set_pair_commutation(self, FirstLetterSet: set, SecondLetterSet: set, AllDistinct = False) -> bool:
        #This method takes two sets of characters in self.alphabet and checks whether each letter in the first set commutes with each letter in the second set.
        #Optionally, it tests whether the two sets are disjoint. In our use cases, an uncancelable letter appearing in a word must be preceded by another letter that creates an uncancelable pair.
        #Therefore, AllDistinct = True will sometimes serve to prune states that we will not use.

        if AllDistinct and (FirstLetterSet.intersection(SecondLetterSet) != set()):
            return(False)
        for LetterPair in product(FirstLetterSet, SecondLetterSet):
            if not LetterPair[0] in (self.c_map[LetterPair[1]].union({LetterPair[1]})):
                return(False)
        return(True)
       
        

    
