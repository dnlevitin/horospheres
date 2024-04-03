from _collections_abc import Sequence, Iterable
from abc import ABC
from sage.combinat.finite_state_machine import FiniteStateMachine, FSMState, FSMTransition, Automaton
from sage.combinat.subset import powerset
from sage.graphs.graph import Graph
from sage.graphs.cliquer import clique_number
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
import copy
from words import WordGenerator, HorocyclicWord
from concatable_automaton import ConcatableAutomaton
from rips_fsm_generator import Rips_FSM_Generator
from divergence_fsm_generator import Divergence_FSM_Generator

class DivergenceHorosphereGenerator:
    def __init__(self, commutation_dict: dict[str, set], order_dict: dict[str, int], ray: tuple[str]):
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray
        self.fsm_gen = Divergence_FSM_Generator(self.c_map, self.o_map, self.ray)
        self.horocyclic_suffix_machine_1234 = self.fsm_gen.horocyclic_suffix_machine_1234()
        self.horocyclic_suffix_machine_1256 = self.fsm_gen.horocyclic_suffix_machine_1256()
        self.shortlex_machine = self.fsm_gen._Rips_FSM_Generator__shortlex_machine()
        self.geodesic_machine = self.fsm_gen._Rips_FSM_Generator__geodesic_machine()
        self.geodesic_suffix_machine = self.fsm_gen.geodesic_suffix_machine()
        self.word_gen = WordGenerator(self.c_map, self.o_map)

        #These dictionaries will keep track of which letters appear in which subwords of horocyclic suffixes.
        self.SubwordDict1234 = {}
        self.SubwordDict1256 = {}
        self.SubwordDictDifferentLength = {}
        #The letters that commute with both ray letters and precede the second one appear first in w_1
        for letter in self.c_map[self.ray[0]].intersection(self.fsm_gen.lesser_star[self.ray[1]]):
            self.SubwordDict1234[letter] = 1
            self.SubwordDict1256[letter] = 1
            self.SubwordDictDifferentLength[letter] = 1
        #The letters that commute with both ray letters and precede only the first appear first in w_2
        for letter in self.fsm_gen.lesser_star[self.ray[0]].intersection(self.fsm_gen.greater_star[self.ray[1]]):
            self.SubwordDict1234[letter] = 2
            self.SubwordDict1256[letter] = 2
            self.SubwordDictDifferentLength[letter] = 2
        #For words of the form w_1w_2w_3w_4, the letters that commute with and precede the second ray letter, but do not commute with the first, appear in w_3.
        for letter in self.fsm_gen.lesser_star[self.ray[1]].difference(self.c_map[self.ray[0]]):
            self.SubwordDict1234[letter] = 3
        #All the rest appear only in w_4
        for letter in self.fsm_gen.alphabet.difference(self.fsm_gen.lesser_star[self.ray[1]].union(self.fsm_gen.lesser_star[self.ray[0]].intersection(self.c_map[self.ray[1]]))):
            self.SubwordDict1234[letter] = 4
        #For words of the form w_1w_2w_5w_6, the letters that commute with and precede the first ray letter, but do not commute with the second, appear in w_5
        for letter in self.fsm_gen.lesser_star[self.ray[0]].difference(self.c_map[self.ray[1]]):
            self.SubwordDict1256[letter] = 3
        #All the rest appear only in w_6
        for letter in self.fsm_gen.alphabet.difference(self.fsm_gen.lesser_star[self.ray[0]].union(self.fsm_gen.lesser_star[self.ray[1]].intersection(self.c_map[self.ray[0]]))):
            self.SubwordDict1256[letter] = 4
        #For pairs of words of different length, every other letter will be in subword 3.
        for letter in self.alphabet:
            try:
                self.SubwordDictDifferentLength[letter]
            except KeyError:
                self.SubwordDictDifferentLength[letter] = 3

        self.same_length_edge_checker1234 = self.fsm_gen.horocyclic_edge_checker(self.SubwordDict1234)
        self.same_length_edge_checker1256 = self.fsm_gen.horocyclic_edge_checker(self.SubwordDict1256)
        self.different_length_edge_checker = self.fsm_gen.horocyclic_edge_checker(self.SubwordDictDifferentLength)
        
        #Create a version of self.fsm_gen.lesser_star that can serve as the defining object for the constructor of the Graph class.
        GraphDict = copy.deepcopy(self.fsm_gen.lesser_star)
        for letter in GraphDict.keys():
            #Convert this into a dictionary of lists rather than sets.
            GraphDict[letter] = list(GraphDict[letter])

        self.clique_dimension = Graph(GraphDict, format = 'dict_of_lists').clique_number()
        #self.clique_dimension = self._determine_clique_dimension_recursive(0, self.alphabet)
        # print('Clique Dimension is ', self.clique_dimension)

    def _determine_clique_dimension_recursive(self, running_total: int, allowable_set:set) -> int:
        '''
        A recursive method to determine the clique dimension of the defining graph.

        :param running_total: the number of letters already in the clique.
        :param allowable_set: the collection of letters commuting with those already in the clique.
        :return: the maximum size of a clique containing the letters already included.
        '''

        if allowable_set == set():
            return running_total

        n = running_total
        
        for letter in allowable_set:
            n = max(n, self._determine_clique_dimension_recursive(running_total+1, allowable_set.intersection(self.c_map[letter])))
        return(n)

    def get_all_length_n_horocyclic_suffixes(self, n:int, mode:bool) -> list:
        '''
        Generate the list of horocyclic suffixes of length n or less.

        :param mode: False if the value of the Busemann Function is even, True if odd.

        :return: A list of all horocyclic suffixes for the desired value of the Busemann Function of up to length n.
        '''
        
        if n < 0:
            raise ValueError('The length of desired words should be non-negative.')

        HorocyclicSuffixList = []
        #EvenList = []
        #OddList = []
        Frontier = []

        if mode:
            EvenLengthGenerator = self.horocyclic_suffix_machine_1234
            OddLengthGenerator = self.horocyclic_suffix_machine_1256
        else:
            EvenLengthGenerator = self.horocyclic_suffix_machine_1256
            OddLengthGenerator = self.horocyclic_suffix_machine_1234
        
        #EvenList.append(self.word_gen.horocyclic_word([[], [], [], []]))
        NewWord = self.word_gen.horocyclic_word([[], [], [], []], mode)
        HorocyclicSuffixList.append(NewWord)
        Frontier.append((EvenLengthGenerator.initial_states()[0], 0, NewWord))
        
        #Edge case: n==0

        if n == 0:
            return HorocyclicSuffixList

        for transition in OddLengthGenerator.transitions(OddLengthGenerator.initial_states()[0]):
            NextStateLabel = transition.to_state.label()
            if NextStateLabel[0]:
                #If NextStateLabel[0] is 1, that means that the letter is not in w_1 or w_2. 
                #In particular, the label is of the form (1, (( int, SubwordState), (LetterExcluderState) ) ) where int is 0 for the third subword or 1 for the fourth.
                SubwordList = [[], [], [], []]
                #recall that transition.word_in returns a singleton list.
                SubwordList[2+NextStateLabel[1][0].label()[0]] = [transition.word_in[0]]
            else:
                #If NextStateLabel[0] is 0, that means that the letter is in w_1 or w_2.
                #In particular, the label is of the form (0, (int, SubwordState)) where int is 0 for the first subword or 1 for the second.
                SubwordList = [[], [], [], []]
                #recall that transition.word_in returns a singleton list.
                SubwordList[NextStateLabel[1][0]] = [transition.word_in[0]]
            NewWord = self.word_gen.horocyclic_word(SubwordList, not mode)
            HorocyclicSuffixList.append(NewWord)
            #OddList.append(ResultingWord)
            Frontier.append((transition.to_state, 1, NewWord))

        #We will lengthen words 2 letters at a time.
        while Frontier:
            state, depth, word = Frontier.pop(0)
            if depth > n-2:
                continue
            if depth%2:
                for FirstTransition in OddLengthGenerator.transitions(state):
                    for SecondTransition in OddLengthGenerator.transitions(FirstTransition.to_state):
                        NewWord = word.copy()

                        #Append the first letter to the relevant subword
                        if FirstTransition.to_state.label()[0]:
                            NewWord.append(FirstTransition.word_in[0], 2+FirstTransition.to_state.label()[1][0].label()[0])
                        else:
                            NewWord.append(FirstTransition.word_in[0], FirstTransition.to_state.label()[1][0])
                            
                        #Append the second letter to the relevant subword.
                        if SecondTransition.to_state.label()[0]:
                            NewWord.append(SecondTransition.word_in[0], 2+SecondTransition.to_state.label()[1][0].label()[0])
                        else:
                            NewWord.append(SecondTransition.word_in[0], SecondTransition.to_state.label()[1][0])
                            
                        HorocyclicSuffixList.append(NewWord)
                        Frontier.append((SecondTransition.to_state, depth+2, NewWord))
                        #OddList.append(NewWord)
            else:
                for FirstTransition in EvenLengthGenerator.transitions(state):
                    for SecondTransition in EvenLengthGenerator.transitions(FirstTransition.to_state):
                        NewWord = word.copy()

                        #Append the first letter to the relevant subword
                        if FirstTransition.to_state.label()[0]:
                            NewWord.append(FirstTransition.word_in[0], 2+FirstTransition.to_state.label()[1][0].label()[0])
                        else:
                            NewWord.append(FirstTransition.word_in[0], FirstTransition.to_state.label()[1][0])
                            
                        #Append the second letter to the relevant subword.
                        if SecondTransition.to_state.label()[0]:
                            NewWord.append(SecondTransition.word_in[0], 2+SecondTransition.to_state.label()[1][0].label()[0])
                        else:
                            NewWord.append(SecondTransition.word_in[0], SecondTransition.to_state.label()[1][0])
                            
                        HorocyclicSuffixList.append(NewWord)
                        Frontier.append((SecondTransition.to_state, depth+2, NewWord))
                        #EvenList.append(NewWord)

        return HorocyclicSuffixList
            
    def calculate_same_length_divergence_adjacencies(self, HorocyclicSuffix:HorocyclicWord) ->list:
        '''
        Given a horocyclic suffix, find all horocyclic suffixes of the same length on the same horosphere such that there is an edge between the two in the divergence graph. 
        
        :param HorocyclicSuffix: A horocyclic suffix.
        :return: The list of all horocyclic suffixes of the same length as HorocyclicSuffix such that the two have close successors.
        '''

        BacktrackedWords = []
        CandidateList = []
        
        #Forbidding loops in the graph.
        FinishedWords = [HorocyclicSuffix]
        
        Adjacencies = []

        # print('finding same length adjacencies for the word', HorocyclicSuffix.SubwordList)

        #We construct the list of horocyclic suffixes of the same length and at distance at most self.clique_dimension away.
        #We begin by deleting letters from HorocyclicSuffix

        #Edge case: HorocyclicSuffix is short enough that it backtracks all the way to the identity.
        if len(HorocyclicSuffix) <= self.clique_dimension:
            # print('This word backtracks all the way to the identity')
            BacktrackedWords = [self.word_gen.horocyclic_word([[],[],[],[]], HorocyclicSuffix.mode)]
        else:
            BacktrackedWords = self._backtracking_recursive(HorocyclicSuffix, self.clique_dimension, self.shortlex_machine.initial_states()[0])

        #We can follow this word by any geodesic word, as long as the result is still a suffix. This will be be potentially highly non-unique, but it is not obvious how to avoid repetition
        for word in BacktrackedWords:
            CandidateList.extend(self._geodesic_successor_horocyclic_suffixes(word, min(len(HorocyclicSuffix),self.clique_dimension), self.geodesic_suffix_machine.process(word.word_as_list, check_epsilon_transitions = False)[1]))

        # print('The list of candidates is ', CandidateList)
        while len(CandidateList) > 0:
            CurrentCandidate = CandidateList.pop(0)
            if CurrentCandidate in FinishedWords:
                continue

            #The edge checker machine wants an input tape that consists of pairs of characters.
            InputList = list(zip(HorocyclicSuffix.word_as_list+['-'], CurrentCandidate.word_as_list+['-']))
            
            # print ('input pair ', HorocyclicSuffix.SubwordList, ' and ', CurrentCandidate.SubwordList)
            # print ('The zipped input is ', InputList)
            if HorocyclicSuffix.mode:
                #These assertions work fine, but then we get an error saying that this state does not belong to a finite state machine.
                #assert(self.same_length_edge_checker1234.has_state(( (), (), (),  (), (), (), (), (), (), tuple(self.alphabet), (1, 1), True )))
                InputAccepted, EndState = self.same_length_edge_checker1234.process(InputList, check_epsilon_transitions = False)[:2]
            else:
                #These assertions work fine, but then we get an error saying that this state does not belong to a finite state machine.
                #assert(self.same_length_edge_checker1256.has_state(( (), (), (),  (), (), (), (), (), (), tuple(self.alphabet), (1, 1), True )))
                InputAccepted, EndState = self.same_length_edge_checker1256.process(InputList, check_epsilon_transitions = False)[:2]
            if not InputAccepted:
                FinishedWords.append(CurrentCandidate)
                continue

            #The same length edge checker only tells us that no non-cancelable pair has been created.
            #To check whether the two have close successors, we need to check whether there is an infinite alternation of some pair of letters as described in Proposition 5.2.10

            CancelingWord = EndState.label()[6]
            #If the cancelable letters were part of the second word (CurrentCandidate) then it is the first word (HorocyclicSuffix) that needs to be elongated to achieve full cancelation
            if EndState.label()[11]:
                ElongatedWord = HorocyclicSuffix.word_as_list + list(CancelingWord)
                NonElongatedWord = CurrentCandidate.word_as_list
            #Otherwise, it is CurrentCandidate that needs to be elongated.
            else:
                ElongatedWord = CurrentCandidate.word_as_list + list(CancelingWord)
                NonElongatedWord = HorocyclicSuffix.word_as_list
                
            if HorocyclicSuffix.mode:
                relevant_suffix_machine = self.horocyclic_suffix_machine_1234
            else:
                relevant_suffix_machine = self.horocyclic_suffix_machine_1256
            ElongatedState = relevant_suffix_machine.process(ElongatedWord, check_epsilon_transitions = False)[1]
            NonElongatedState = relevant_suffix_machine.process(NonElongatedWord, check_epsilon_transitions = False)[1]
            
            LettersCommutingWithClique = set(EndState.label()[9])
            #Check whether any of these letters is permitted by both the above states.

            # print('Processing pair ', HorocyclicSuffix.SubwordList, CurrentCandidate.SubwordList)
            # print('The elongated word is ', ElongatedWord, ' and the non-elongated word is ', NonElongatedWord)
            # print('The state of the elongated word is ', ElongatedState.label())
            # print('Its outgoing transitions are ', relevant_suffix_machine.transitions(ElongatedState))
            
            #Recall that transition.word_in outputs a list containing the label of the transition, not the label itself.
            LettersAcceptedFromElongatedState = {transition.word_in[0] for transition in relevant_suffix_machine.iter_transitions(ElongatedState)}
            #ElongatedTransitionDict = relevant_suffix_machine.transition_dict(ElongatedState)
            LettersAcceptedFromNonElongatedState = {transition.word_in[0] for transition in relevant_suffix_machine.iter_transitions(NonElongatedState)}
            #NonElongatedTransitionDict = relevant_suffix_machine.transition_dict(NonElongatedState)
        
            for letter in LettersCommutingWithClique:
                if letter in LettersAcceptedFromElongatedState.intersection(LettersAcceptedFromNonElongatedState) and LettersCommutingWithClique.difference(self.c_map[letter].union({letter})) != set():
                    Adjacencies.append(CurrentCandidate)
                    break
            FinishedWords.append(CurrentCandidate)
                    
        return Adjacencies

    def calculate_shorter_divergence_adjacencies(self, HorocyclicSuffix:HorocyclicWord) ->list:
        '''
        Given a horocyclic suffix, find all shorter horocyclic on the same horosphere such that there is an edge between the two in the divergence graph. 
        Usually, this method uses the various stored horocyclic_suffix_machine's. However, some care is required in the case that the extra prefix letters are cancelable.

        :param HorocyclicSuffix: A horocyclic suffix.
        :return: The list of all horocyclic suffixes of shorter than HorocyclicSuffix such that the two have close successors.
        '''

        Adjacencies = []

        #If there are any other letters besides these, then between this suffix and any shorter suffix there will always be an uncancelable pair
        AcceptableLetters = self.c_map[self.ray[1-int(HorocyclicSuffix.mode)]]
        
        #edge case: HorocyclicSuffix is empty
        if HorocyclicSuffix.word_as_list == []:
            return Adjacencies

        if HorocyclicSuffix[2] != []:
            return Adjacencies

        for letter in HorocyclicSuffix[3]:
            if not letter in AcceptableLetters:
                return Adjacencies
            
        # print('Finding shorter divergence adjacencies for ', HorocyclicSuffix.SubwordList)
        
        BacktrackedWords = []
        CandidateList = []
        FinishedWords = []

        #This list will keep track of the letters to add to the shorter word. 
        #The horocyclic suffix mode tells us the last letter of the prefix associated to HorocyclicSuffix. It is self.ray[0] if HorocyclicSuffix.mode is False, or self.ray[1] if HorocyclicSuffix.mode is True.
        #Therefore, the 0th letter of the shorter word is self.ray[1] if HorocyclicSuffix.mode is False, or self.ray[0] if HorocyclicSuffix.mode is True.
        #Further extra letters alternate thereafter.
        ExtensionList = []
        for length in range(0, self.clique_dimension):
            if HorocyclicSuffix.mode ^ length%2:
                ExtensionList.append(self.ray[0])
            else:
                ExtensionList.append(self.ray[1])
        
        if HorocyclicSuffix[3] == []:
            #If so, then every letter of HorocyclicSuffix commutes with both self.ray[0] and self.ray[1], so that they all commute with one another.
            #Therefore, these words backtrack all the way to the identity.
            # print('This word has no third or fourth subword')
            CandidateList = self.get_all_length_n_horocyclic_suffixes(len(HorocyclicSuffix)-1, not (HorocyclicSuffix.mode ^ (len(HorocyclicSuffix)%2)))

        else:
            #In this case, the only shorter words that HorocyclicSuffix can be adjacent to are words that are 1 letter shorter. These must all be of the opposite form to HorocyclicSuffix
            if len(HorocyclicSuffix) < self.clique_dimension:
                BacktrackedWords = [self.word_gen.horocyclic_word([[],[],[],[]], not HorocyclicSuffix.mode)]
            else:
                StartingWord = self._switch_form_special_case(HorocyclicSuffix)
                BacktrackedWords = self._backtracking_recursive(StartingWord, self.clique_dimension, self.shortlex_machine.initial_states()[0])
                                
            for word in BacktrackedWords:
                BacktrackedState = self.geodesic_suffix_machine.process(word.word_as_list, check_epsilon_transitions = False)[1]
                # print('The backtracked word is ', word.SubwordList, ', and its state in the geodesic suffix machine is ', BacktrackedState.label())
                CandidateList.extend(self._geodesic_successor_horocyclic_suffixes(word, min(len(HorocyclicSuffix),self.clique_dimension)-1, BacktrackedState))
            
        # print('The candidate list is', CandidateList)

        while CandidateList:
            CurrentCandidate = CandidateList.pop(0)
            if CurrentCandidate in FinishedWords:
                continue

            #Issue: Because of the value of SubwordDictUnequalLength evaluated at ray letters, this does not always produce a correct output
            #Workaround: calculate directly the desired output in the case where the length differs by more than 1.
            #If the length differs by 1, bifurcate based on whether the extra prefix letter can be canceled.

            CandidateInput = CurrentCandidate[0] + CurrentCandidate[1] + CurrentCandidate[2] + ExtensionList[0:len(HorocyclicSuffix)-len(CurrentCandidate):] + CurrentCandidate[3]
            InputList = list(zip(HorocyclicSuffix.word_as_list+['-'], CandidateInput+['-']))

            (InputAccepted, EndState) = self.different_length_edge_checker.process(InputList, check_epsilon_transitions = False)

            if InputAccepted and EndState is None:
                raise RuntimeError('The pair ', HorocyclicSuffix, ' and ', CandidateInput, 'yields an unprocessable accepted input')

            if not InputAccepted:
                FinishedWords.append(CurrentCandidate)
                continue

            #The same length edge checker only tells us that no non-cancelable pair has been created.
            #To check whether the two have close successors, we need to check whether there is an infinite alternation of some pair of letters as described in Proposition 5.2.10

            CancelingWord = EndState.label()[4]

            #The CancelingWord will be written after either HorocyclicSuffix or CandidateWord, depending on which word the cancelable letters belong to.
            #However, some of the letters of the CancelingWord may have been prefix letters, and if so, writing them does not change the suffix.
            #Since we are keeping track of edges between suffixes, we must first process CancelingWord slightly.
            #Recall that if the final state has True in index 11, it means that the second input contains cancelable letters, including perhaps a prefix letter.
            #Note that the uncanceled letters between subwords 1 and 2 will always be uncancelable no matter what. So if prefix letters can be canceled, they must appear at the beginning of the cancelable word.

            if EndState.label()[11]:
                if HorocyclicSuffix[3] == 0:
                    #In this case, every extra prefix letter will appear in the cancelable set, but we want to drop all of them.
                    CancelingWord = CancelingWord[len(HorocyclicSuffix)-len(CurrentCandidate)::]
                elif ExtensionList[0] in self.alphabet.intersection(*[self.fsm_gen.lesser_star[letter] for letter in HorocyclicSuffix[3]]):
                    #In this case, there is 1 extra prefix letter.
                    CancelingWord = CancelingWord[1::]
                    
                #Otherwise, the extra prefix letter is in the uncancelable set, so there is no need to worry about it.


             
            if HorocyclicSuffix.mode:
                if EndState.label()[11]:
                    # print ('input pair ', HorocyclicSuffix, ' and ', CandidateInput, ' with canceling word ', CancelingWord)
                    HorocyclicState = self.horocyclic_suffix_machine_1234.process(HorocyclicSuffix.word_as_list + list(CancelingWord), check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1234.next_letters(HorocyclicState)
                else:
                    HorocyclicState = self.horocyclic_suffix_machine_1234.process(HorocyclicSuffix.word_as_list, check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1234.next_letters(HorocyclicState)
            else:
                if EndState.label()[11]:
                    HorocyclicState = self.horocyclic_suffix_machine_1256.process(HorocyclicSuffix.word_as_list + list(CancelingWord), check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1256.next_letters(HorocyclicState)
                else:
                    HorocyclicState = self.horocyclic_suffix_machine_1256.process(HorocyclicSuffix.word_as_list, check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1256.next_letters(HorocyclicState)

            if CurrentCandidate.mode:
                if EndState.label()[11]:
                    CandidateState = self.horocyclic_suffix_machine_1234.process(CurrentCandidate.word_as_list, check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1234.next_letters(CandidateState)
                else:
                    CandidateState = self.horocyclic_suffix_machine_1234.process(CurrentCandidate.word_as_list+ list(CancelingWord), check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1234.next_letters(CandidateState)
            else:
                if EndState.label()[11]:
                    CandidateState = self.horocyclic_suffix_machine_1256.process(CurrentCandidate.word_as_list, check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1256.next_letters(CandidateState)
                else:
                    CandidateState = self.horocyclic_suffix_machine_1256.process(CurrentCandidate.word_as_list+ list(CancelingWord), check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1256.next_letters(CandidateState)

            LettersCommutingWithClique = set(EndState.label()[9])
            #Check whether any of these letters is permitted by both the above states.
        
            for letter in LettersCommutingWithClique:

                #Check if there is another letter in the alphabet which does not commute with the given letter
                if letter in HorocyclicNextLetters.intersection(CandidateNextLetters) and LettersCommutingWithClique.difference(self.c_map[letter].union({letter})) != set():
                    Adjacencies.append(CurrentCandidate)
                    break
            FinishedWords.append(CurrentCandidate)
                    
        return Adjacencies
        
    def calculate_divergence_adjacencies(self, HorocyclicSuffix:HorocyclicWord) -> list:
        """
        Use "calculate_same_length_divergence_adjacencies" and "calculate_shorter_divergence_adjacencies" to find all adjacent words which are at most as long as suffix.

        :param HorocyclicSuffix: A horocyclic suffix.
        :return: All adjacent suffixes at most as long as "suffix".
        """

        adjacencies = []
        
        adjacencies.extend(self.calculate_same_length_divergence_adjacencies(HorocyclicSuffix))
        adjacencies.extend(self.calculate_shorter_divergence_adjacencies(HorocyclicSuffix))
        
        return adjacencies

    def calculate_divergence_horosphere_edges(self, HorocyclicSuffix_list: list) -> list:
        """
        Calculate the set of edges from entries of suffix_list to shorter suffixes.

        :param HorocyclicSuffix_list: A list of horocyclic suffixes.
        :return: A list of all pairs of horocyclic suffixes whose corresponding words have close successors for all time 
        such that the first is an entry of HorocyclicSuffix_list and the second is no longer than the first.
        """

        edges = []

        for suffix in HorocyclicSuffix_list:
            for newsuffix in self.calculate_divergence_adjacencies(suffix):
                edges.append( (str(suffix), str(newsuffix)))
        return(edges)
        
    def horosphere_as_networkx(self, length: int, BusemannValue: int):
        suffixes = self.get_all_length_n_horocyclic_suffixes(length, bool(BusemannValue % 2))
        print(f"Suffixes of length {length} calculated: \n\t\t {len(suffixes)} words found")
        print(suffixes)
        edges = self.calculate_divergence_horosphere_edges(suffixes)
        print(f"Words processing completed: \n\t\t {len(suffixes)} words processed")
        print(edges)

        G = nx.Graph()
        G.add_edges_from(edges)
        print(f"Length {length} Horosphere generated: \n\t\t {G}")
        return G

    def _backtracking_recursive(self, word:HorocyclicWord, StepCount:int, ShortlexState:FSMState) -> list:
        '''
        Recursively find all horocyclic suffixes word' so that, as geodesic words word=word' + tail, where tail is a shortlex word StepCount letters long.
        The assumption that tail is shortlex is only relevant to make the outputs unique.

        :param word: the word that has been reached so far.
        :param StepCount: the number of backtracking steps that still remain.
        :param ShortlexState: the current state in the shortlex machine 
        :return: a list without repetition of the HorocyclicWords word' as above.
        '''

        if StepCount == 0:
            return([word])

        ResultingWords = []
        #We backtrack by the letters that are both final letters of word and still allowed by the shortlex state.
        LastLetters = set(self.geodesic_machine.process(word.word_as_list, check_epsilon_transitions = False)[1].label())
        for transition in self.shortlex_machine.transitions(ShortlexState):
            #Recall that transition.word_in outputs a list containing the label of the transition, not the label itself. 
            if transition.word_in[0] in LastLetters:
                for i in reversed(range(0,4)):
                    if transition.word_in[0] in set(word[i]):
                        NewSubwordList = copy.deepcopy(word.SubwordList)
                        ReversedSubword = copy.deepcopy(word[i])[::-1]
                        deletion_index = ReversedSubword.index(transition.word_in[0])
                        DeletedSubword = (ReversedSubword[0:deletion_index:]+ReversedSubword[deletion_index+1::])[::-1]
                        NewSubwordList[i] = DeletedSubword
                        NewWord = self.word_gen.horocyclic_word(NewSubwordList, word.mode)
                        break
                ResultingWords.extend(self._backtracking_recursive(NewWord, StepCount-1, transition.to_state))
        return ResultingWords

    def _geodesic_successor_horocyclic_suffixes(self, word:HorocyclicWord, StepCount:int, GeodesicSuffixState:FSMState) -> list:
        '''
        Recursively find all horocyclic suffixes word' that are StepCount letters longer than word, such that word' is a geodesic successor to word.

        :param word: the successor that has been reached so far.
        :param StepCount: the number of letters still to write.
        :param GeodesicSuffixState: the state of word in the geodesic suffix machine.
        :return: a list with repetition of all the HorocyclicWords word' as above.
        '''
        
        if StepCount == 0:
            return [word]
        
        if StepCount < 0:
            raise ValueError('Cannot go a negative number of steps forward. Use the _backtracking_recursive function to go backwards.')
        
        ResultingWords = []  
        
        for transition in self.geodesic_suffix_machine.transitions(GeodesicSuffixState):
            #determine which subword transition.word_in should be inserted into. Recall that transition.word_in is a singleton list
            if word.mode:
                EarliestPossibleSubword = self.SubwordDict1234[transition.word_in[0]]
            else:
                EarliestPossibleSubword = self.SubwordDict1256[transition.word_in[0]]
            
            for i in reversed(range(EarliestPossibleSubword-1,4)):
                #transition.word_in belongs in subword i either if it cannot commute to an earlier subword, or if subword i is the earliest subword the letter is allowed in.
                if i == EarliestPossibleSubword-1 or (not self.fsm_gen._test_set_pair_commutation({transition.word_in[0]},set(word[i]))):
                    NewSubwordList = copy.deepcopy(word.SubwordList)
                    NewSubword = self.word_gen.word(word[i])
                    #Recall that transition.word_in is a singleton list.
                    NewSubword.shortlex_append(transition.word_in[0])
                    NewSubwordList[i] = NewSubword.word_as_list
                    NewWord = self.word_gen.horocyclic_word(NewSubwordList, word.mode)
                    break
            ResultingWords.extend(self._geodesic_successor_horocyclic_suffixes(NewWord, StepCount-1, transition.to_state))
            
        return ResultingWords

    def _switch_form_special_case(self, word:HorocyclicWord) -> HorocyclicWord:
        '''
        Given a horocyclic suffix of form 1234, return an equal horocyclic suffix of form 1256, or vice versa.
        Only implemented in the case that subword 3 is empty
        and that subword 4 consists of letters commuting with the ray letter that is between word_5 and word_6 if word is of form 1234, or vice versa.
    
        With this assumption, once a letter of word[4] is read that follows this ray letter, no letter preceding the ray letter can be written until a letter is written that does not commute with it
        Therefore, the first time a letter of word[4] follows the relevant ray letter is the break between the resulting subwords.
        This takes linear time to computer. Without the assumption, it would take quadratic time.
    
        :param word: A HorocyclicWord with empty third subword and subword 4 satisfying the condition above.
        :return: An equivalent HorocyclicWord of the opposite form to that of word.
        
        '''
    
        if word[2] != []:
            raise ValueError('Not implemented in the general case')
    
        #We will need to insert a letter into the fourth subword of word.
        #If word is of the form 1234, then the letter to be inserted is self.ray[0], and vice versa.
        SplitLetter = self.ray[1-int(word.mode)]
        
        #sentinel value
        SplitIndex = None
        
        for index in  range(0, len(word[3])):
            if not word[3][index] in self.c_map[SplitLetter]:
                raise ValueError('Not implemented in the general case')
            if self.o_map[word[3][index]] > self.o_map[SplitLetter] and SplitIndex is None:
                SplitIndex = index
                
        #At the end of either loop, SplitIndex records either the first instance of a letter commuting with and following SplitLetter
        #Or, if each letter commutes with and precedes SplitLetter, then SplitIndex still has the sentinel value None.
        if SplitIndex is None:
            NewWord = self.word_gen.horocyclic_word([word[0], word[1], word[3], []], not word.mode)
        else:
            NewWord = self.word_gen.horocyclic_word([word[0], word[1], word[3][:SplitIndex:], word[3][SplitIndex::]], not word.mode)
    
        return NewWord