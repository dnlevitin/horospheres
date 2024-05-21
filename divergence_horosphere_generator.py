from sage.combinat.finite_state_machine import FSMState
from sage.graphs.graph import Graph
import networkx as nx
import copy
from words import WordGenerator, HorocyclicWord
from divergence_fsm_generator import DivergenceFSMGenerator


class DivergenceHorosphereGenerator:


    '''
    This object will generate the divergence graph on a horosphere of a
     with a desired value of the Busemann function.
    '''

    def __init__(self, commutation_dict: dict[str, set], 
                 order_dict: dict[str, int], ray: tuple[str]):
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray
        self.fsm_gen = DivergenceFSMGenerator(self.c_map, self.o_map, self.ray)
        self.horocyclic_suffix_machine_1234 = \
            self.fsm_gen.horocyclic_suffix_machine_1234()
        self.horocyclic_suffix_machine_1256 = \
            self.fsm_gen.horocyclic_suffix_machine_1256()
        self.shortlex_machine = self.fsm_gen.shortlex_machine()
        self.geodesic_machine = self.fsm_gen.geodesic_machine()
        self.geodesic_suffix_machine = self.fsm_gen.geodesic_suffix_machine()
        self.word_gen = WordGenerator(self.c_map, self.o_map)

        # These dictionaries will keep track of which letters appear in 
        # which subwords of horocyclic suffixes.
        self.subword_dict_1234 = {}
        self.subword_dict_1256 = {}
        self.subword_dict_different_length = {}
        # The letters that commute with both ray letters and precede the 
        # second one appear first in w_1.
        for letter in self.c_map[self.ray[0]].intersection(
          self.fsm_gen.lesser_star[self.ray[1]]):
            self.subword_dict_1234[letter] = 1
            self.subword_dict_1256[letter] = 1
            self.subword_dict_different_length[letter] = 1
        # The letters that commute with both ray letters and precede 
        # only the first appear first in w_2.
        for letter in self.fsm_gen.lesser_star[self.ray[0]]\
          .intersection(self.fsm_gen.greater_star[self.ray[1]]):
            self.subword_dict_1234[letter] = 2
            self.subword_dict_1256[letter] = 2
            self.subword_dict_different_length[letter] = 2
        # For words of the form w_1w_2w_3w_4, the letters that commute 
        # with and precede the second ray letter, but do not commute 
        # with the first, appear in w_3.
        for letter in self.fsm_gen.lesser_star[self.ray[1]]\
          .difference(self.c_map[self.ray[0]]):
            self.subword_dict_1234[letter] = 3
        # All the rest appear only in w_4.
        for letter in self.fsm_gen.alphabet.difference(
            self.fsm_gen.lesser_star[self.ray[1]]\
            .union(self.fsm_gen.lesser_star[self.ray[0]]
                   .intersection(self.c_map[self.ray[1]])
                   )):
            self.subword_dict_1234[letter] = 4
        # For words of the form w_1w_2w_5w_6, the letters that commute
        # with and precede the first ray letter, but do not commute with
        # the second, appear in w_5.
        for letter in self.fsm_gen.lesser_star[self.ray[0]]\
          .difference(self.c_map[self.ray[1]]):
            self.subword_dict_1256[letter] = 3
        # All the rest appear only in w_6.
        for letter in self.fsm_gen.alphabet.difference(
            self.fsm_gen.lesser_star[self.ray[0]]\
            .union(self.fsm_gen.lesser_star[self.ray[1]]
                   .intersection(self.c_map[self.ray[0]])
                   )):
            self.subword_dict_1256[letter] = 4
        # For pairs of words of different length, every other letter 
        # will be in subword 3.
        for letter in self.alphabet:
            try:
                self.subword_dict_different_length[letter]
            except KeyError:
                self.subword_dict_different_length[letter] = 3

        self.same_length_edge_checker1234 = self.fsm_gen.horocyclic_edge_checker(
            self.subword_dict_1234)
        self.same_length_edge_checker1256 = self.fsm_gen.horocyclic_edge_checker(
            self.subword_dict_1256)
        self.different_length_edge_checker = self.fsm_gen.horocyclic_edge_checker(
            self.subword_dict_different_length)
        
        # Create a version of `self.fsm_gen.lesser_star` that can serve 
        # as the defining object for the constructor of a `Graph`.
        graph_dict = copy.deepcopy(self.fsm_gen.lesser_star)
        for letter in graph_dict.keys():
            #Convert this into a dictionary of lists rather than sets.
            graph_dict[letter] = list(graph_dict[letter])

        self.clique_dimension = Graph(graph_dict, 
                                      format = 'dict_of_lists'
                                      ).clique_number()
        
        # When finding edges between horocyclic suffixes of different
        # lengths, these lists will keep track of the prefix letters 
        # that must be added to the shorter word, depending on the mode
        # of the shorter word. 
        # `extension_list` will be a list of lists. `extension_list[0]`
        # will be a list that starts with `self.ray[0]`, and alternate
        # thereafter. `extension_list[1]` will be a list that starts 
        # with `self.ray[1]` and alternate thereafter.
        self.extension_list = [[],[]]
        for length in range(0, self.clique_dimension):
            self.extension_list[0].append(self.ray[length%2])
            self.extension_list[1].append(self.ray[(length+1)%2])

    def get_all_length_n_horocyclic_suffixes(self, n:int, mode:bool) -> list:
        '''
        Generate the list of horocyclic suffixes of length n or less.

        :param mode: False if the value of the Busemann Function is 
         even, True if odd.

        :return: A list of all horocyclic suffixes for the desired value
         of the Busemann Function of up to length `n`.
        '''
        
        if n < 0:
            raise ValueError('The length of desired words should be \
                             non-negative.')

        horocyclic_suffix_list = []
        frontier = []

        if mode:
            even_length_generator = self.horocyclic_suffix_machine_1234
            odd_length_generator = self.horocyclic_suffix_machine_1256
        else:
            even_length_generator = self.horocyclic_suffix_machine_1256
            odd_length_generator = self.horocyclic_suffix_machine_1234

        new_word = self.word_gen.horocyclic_word([[], [], [], []], mode)
        horocyclic_suffix_list.append(new_word)
        #The Theta graph case throws an IndexError here. the machine does not have any initial states.
        frontier.append((even_length_generator.initial_states()[0], 0, new_word))
        
        # Edge case: `n==0`.
        if n == 0:
            return horocyclic_suffix_list

        for transition in odd_length_generator.transitions(
          odd_length_generator.initial_states()[0]):
            next_state_label = transition.to_state.label()
            if next_state_label[0]:
                # If `next_state_label[0]` is `1`, that means that the 
                # letter is not in w_1 or w_2. In particular, the label
                # is of the form 
                # `(1,((int, subword_state),(letter_excluder_state)))`,
                # where `int` is `0` for the third subword or `1` for
                # the fourth.
                subword_list = [[], [], [], []]
                # Recall that `transition.word_in` returns a singleton
                # list.
                subword_list[2+next_state_label[1][0].label()[0]] = \
                    [transition.word_in[0]]
            else:
                # If `next_state_label[0]` is `0`, that means that the 
                # letter is in w_1 or w_2.
                # In particular, the label is of the form 
                # `(0,(int,subword_state))` where `int` is `0 `for the
                # first subword or `1` for the second.
                subword_list = [[], [], [], []]
                # Recall that transition.word_in returns a singleton
                # list.
                subword_list[next_state_label[1][0]] = [transition.word_in[0]]
            new_word = self.word_gen.horocyclic_word(subword_list, not mode)
            horocyclic_suffix_list.append(new_word)
            frontier.append((transition.to_state, 1, new_word))

        # We will lengthen words 2 letters at a time.
        while frontier:
            state, depth, word = frontier.pop(0)
            if depth > n-2:
                continue
            if depth%2:
                for first_transition in odd_length_generator.transitions(state):
                    for second_transition in odd_length_generator.transitions(
                      first_transition.to_state):
                        new_word = word.copy()

                        # Append the first letter to the relevant
                        # subword.
                        if first_transition.to_state.label()[0]:
                            new_word.append(first_transition.word_in[0],
                                            2+first_transition.to_state\
                                                .label()[1][0].label()[0])
                        else:
                            new_word.append(first_transition.word_in[0],
                                            first_transition.to_state\
                                                .label()[1][0])
                            
                        # Append the second letter to the relevant
                        # subword.
                        if second_transition.to_state.label()[0]:
                            new_word.append(second_transition.word_in[0],
                                            2+second_transition.to_state\
                                                .label()[1][0].label()[0])
                        else:
                            new_word.append(second_transition.word_in[0],
                                            second_transition.to_state\
                                                .label()[1][0])
                            
                        horocyclic_suffix_list.append(new_word)
                        frontier.append((second_transition.to_state, depth+2,
                                         new_word))
            else:
                for first_transition in even_length_generator.transitions(state):
                    for second_transition in even_length_generator.transitions(
                      first_transition.to_state):
                        new_word = word.copy()

                        # Append the first letter to the relevant 
                        # subword.
                        if first_transition.to_state.label()[0]:
                            new_word.append(first_transition.word_in[0],
                                            2+first_transition.to_state\
                                                .label()[1][0].label()[0])
                        else:
                            new_word.append(first_transition.word_in[0],
                                            first_transition.to_state\
                                                .label()[1][0])
                            
                        # Append the second letter to the relevant 
                        # subword.
                        if second_transition.to_state.label()[0]:
                            new_word.append(second_transition.word_in[0],
                                            2+second_transition.to_state\
                                                .label()[1][0].label()[0])
                        else:
                            new_word.append(second_transition.word_in[0],
                                            second_transition.to_state\
                                                .label()[1][0])
                            
                        horocyclic_suffix_list.append(new_word)
                        frontier.append((second_transition.to_state, depth+2,
                                         new_word))

        return horocyclic_suffix_list
            
    def calculate_same_length_divergence_adjacencies(self, horocyclic_suffix\
                                                     :HorocyclicWord) ->list:
        
        '''
        Given a horocyclic suffix, find all horocyclic suffixes of the 
        same length on the same horosphere such that there is an edge 
        between the two in the divergence graph. 
        
        :param horocyclic_suffix: A horocyclic suffix.
        :return: The list of all horocyclic suffixes of the same length 
         as `horocyclic_suffix` such that the two have close successors.
        '''

        backtracked_words = []
        candidate_list = []
        
        # Forbid loops in the graph.
        finished_words = [horocyclic_suffix]
        
        adjacencies = []

        # print('finding same length adjacencies for the word',
        #       horocyclic_suffix.subword_list)

        # We construct the list of horocyclic suffixes of the same 
        # length and at distance at most `self.clique_dimension` away.
        # We begin by deleting letters from `horocyclic_suffix`.

        # Edge case: `horocyclic_suffix` is short enough that it 
        # backtracks all the way to the identity.
        if len(horocyclic_suffix) <= self.clique_dimension:
            # print('This word backtracks all the way to the identity')
            backtracked_words = [self.word_gen.horocyclic_word(
                [[],[],[],[]], horocyclic_suffix.mode)]
        else:
            backtracked_words = self._backtracking_recursive(
                horocyclic_suffix, self.clique_dimension, 
                self.shortlex_machine.initial_states()[0])

        # We can follow this word by any geodesic word, as long as the 
        # result is still a suffix. This will be be potentially highly
        # non-unique, but it is not obvious how to avoid repetition.
        for word in backtracked_words:
            candidate_list.extend(self._geodesic_successor_horocyclic_suffixes(
                word, min(len(horocyclic_suffix),self.clique_dimension),
                self.geodesic_suffix_machine.process(
                    word.word_as_list, check_epsilon_transitions = False)[1]))

        # print('The list of candidates is ', candidate_list)
        while candidate_list:
            current_candidate = candidate_list.pop(0)
            if current_candidate in finished_words:
                continue

            # The edge checker machine wants an input tape that consists 
            # of pairs of characters.
            input_list = list(zip(horocyclic_suffix.word_as_list+['-'],
                                 current_candidate.word_as_list+['-']))
            
            # print ('input pair ', horocyclic_suffix.subword_list, ' and ',
            #        current_candidate.subword_list)
            # print ('The zipped input is ', input_list)
            if horocyclic_suffix.mode:
                input_accepted, end_state = self.same_length_edge_checker1234\
                    .process(input_list, check_epsilon_transitions = False)[:2]
            else:
                input_accepted, end_state = self.same_length_edge_checker1256\
                    .process(input_list, check_epsilon_transitions = False)[:2]
            if not input_accepted:
                finished_words.append(current_candidate)
                continue

            # The same length edge checker only tells us that no 
            # non-cancelable pair has been created. To check whether the
            # two have close successors, we need to check whether there
            # is an infinite alternation of some pair of letters as 
            # described in Proposition 5.2.10.

            canceling_word = end_state.label()[6]
            
            # These words have shortlex states equivalent to those of
            # the full words corresponding to `horocyclic_suffix` and
            # `current_candidate`.
            if horocyclic_suffix.mode:
                horocyclic_word_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0]]\
                        + horocyclic_suffix[2] + [self.ray[1]]\
                        + horocyclic_suffix[3]
                current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]+ [self.ray[0]]\
                        + current_candidate[2] + [self.ray[1]]\
                        + current_candidate[3]
            else:
                horocyclic_word_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0], 
                                                                  self.ray[1]]\
                        + horocyclic_suffix[2] + [self.ray[0]]\
                        + horocyclic_suffix[3]
                current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]+ [self.ray[0], 
                                                                 self.ray[1]]\
                        + current_candidate[2] + [self.ray[0]]\
                        + current_candidate[3]
                
            
            # If the cancelable letters were part of the second word 
            # `current_candidate` then it is the first word 
            # `horocyclic_suffix` that needs to be elongated to achieve
            # full cancelation.
            if end_state.label()[11]:
                horocyclic_word_equivalent = horocyclic_word_equivalent\
                    + list(canceling_word)
            # Otherwise, it is current_candidate that needs to be 
            # elongated.
            else:
                current_candidate_equivalent = current_candidate_equivalent\
                    + list(canceling_word)
                
            horocyclic_word_state = self.shortlex_machine.process(
                horocyclic_word_equivalent)[1]
            current_candidate_state = self.shortlex_machine.process(
                current_candidate_equivalent)[1]
            
            if horocyclic_word_state.label() is None or \
              current_candidate_state.label() is None:
                raise RuntimeError('The pair of words ', 
                                   horocyclic_suffix.word_as_list,
                                   current_candidate.word_as_list,
                                   'created an elongated word that was\
                                    not accepted by the shortlex machine.\
                                    The mode is ', horocyclic_suffix.mode)
            
            letters_commuting_with_clique = set(end_state.label()[9])
            letters_accepted_from_horocyclic_word = self.alphabet.difference(
                set(horocyclic_word_state.label()))
            letters_accepted_from_current_candidate = self.alphabet.difference(
                set(current_candidate_state.label()))
            
            # Check whether there is a pair of letters commuting with
            # clique, not commuting with one another, and one of the pair
            # permitted by both words. This is the condition that there
            # is an edge between the two in the divergence graph.
            for letter in letters_commuting_with_clique:
                if letter in letters_accepted_from_horocyclic_word.intersection(
                  letters_accepted_from_current_candidate) \
                  and letters_commuting_with_clique.difference(
                  self.c_map[letter].union({letter})) != set():
                    adjacencies.append(current_candidate)
                    break
            finished_words.append(current_candidate)

            '''
            # If the cancelable letters were part of the second word 
            # `current_candidate` then it is the first word 
            # `horocyclic_suffix` that needs to be elongated to achieve
            # full cancelation.
            if end_state.label()[11]:
                elongated_word = horocyclic_suffix.word_as_list\
                    + list(canceling_word)
                non_elongated_word = current_candidate.word_as_list
            # Otherwise, it is current_candidate that needs to be 
            # elongated.
            else:
                elongated_word = current_candidate.word_as_list\
                    + list(canceling_word)
                non_elongated_word = horocyclic_suffix.word_as_list
                
            if horocyclic_suffix.mode:
                relevant_suffix_machine = self.horocyclic_suffix_machine_1234
            else:
                relevant_suffix_machine = self.horocyclic_suffix_machine_1256
            elongated_state = relevant_suffix_machine\
                .process(elongated_word)[1]
            non_elongated_state = relevant_suffix_machine\
                .process(non_elongated_word)[1]
            if (elongated_state.label() is None) or (non_elongated_state.label() is None):
                raise RuntimeError('The pair of words ', horocyclic_suffix.word_as_list,
                                    current_candidate.word_as_list, 'created the elongated word',
                                    elongated_word, 'which was not accepted by the suffix machine. The current state is ',
                                    horocyclic_suffix.mode)
            
            # We will check whether any of these letters is permitted by 
            # both the above states.
            letters_commuting_with_clique = set(end_state.label()[9])
            
            # Recall that `transition.word_in` outputs a list containing
            # the label of the transition, not the label itself.
            letters_accepted_from_elongated_state = {
                transition.word_in[0] for transition in relevant_suffix_machine\
                    .iter_transitions(elongated_state)}
            letters_accepted_from_non_elongated_state = {
                transition.word_in[0] for transition in relevant_suffix_machine\
                    .iter_transitions(non_elongated_state)}
        
            for letter in letters_commuting_with_clique:
                if letter in letters_accepted_from_elongated_state.intersection(
                    letters_accepted_from_non_elongated_state)\
                    and letters_commuting_with_clique.difference(
                        self.c_map[letter].union({letter})) != set():
                    adjacencies.append(current_candidate)
                    break
            finished_words.append(current_candidate)
            '''
        return adjacencies

    def calculate_shorter_divergence_adjacencies(self, horocyclic_suffix\
                                                 :HorocyclicWord) ->list:
        
        '''
        Given a horocyclic suffix, find all shorter horocyclic suffixes
         on the same horosphere such that there is an edge between the
         two in the divergence graph. 
        
        :param horocyclic_suffix: A horocyclic suffix.
        :return: The list of all horocyclic suffixes shorter than
         `horocyclic_suffix` such that the two have close successors.
        '''

        adjacencies = []

        # If there are any other letters besides these, then between 
        # this suffix and any shorter suffix there will always be an 
        # uncancelable pair.
        acceptable_letters = self.c_map[self.ray[1-int(horocyclic_suffix.mode)]]
        
        # Edge case: horocyclic_suffix is empty.
        if horocyclic_suffix.word_as_list == []:
            return adjacencies

        if horocyclic_suffix[2] != []:
            return adjacencies

        for letter in horocyclic_suffix[3]:
            if not letter in acceptable_letters:
                return adjacencies
        
        backtracked_words = []
        candidate_list = []
        finished_words = []

        if horocyclic_suffix[3] == []:
            # If so, then every letter of horocyclic_suffix commutes 
            # with both `self.ray[0]` and `self.ray[1]`, so that they
            # all commute with one another.
            # Therefore, these words backtrack all the way to the 
            # identity.
            candidate_list = self.get_all_length_n_horocyclic_suffixes(
                len(horocyclic_suffix)-1, 
                (horocyclic_suffix.mode ^ bool(len(horocyclic_suffix)%2)))

        else:
            # In this case, the only shorter words that 
            # `horocyclic_suffix` can be adjacent to are words that are
            # 1 letter shorter. These must all be of the opposite form
            # to `horocyclic_suffix`.
            #
            # We first backtrack `self.clique_dimension` steps.
            if len(horocyclic_suffix) < self.clique_dimension:
                backtracked_words = [self.word_gen.horocyclic_word(
                    [[],[],[],[]], not horocyclic_suffix.mode)]
            else:
                starting_word = self._switch_form_special_case(horocyclic_suffix)
                backtracked_words = self._backtracking_recursive(
                    starting_word, self.clique_dimension,
                    self.shortlex_machine.initial_states()[0])

            # Next we take 1 fewer step forward than we backtracked.         
            for word in backtracked_words:
                backtracked_state = self.geodesic_suffix_machine\
                    .process(word.word_as_list)[1]
                candidate_list.extend(
                    self._geodesic_successor_horocyclic_suffixes(
                        word, min(len(horocyclic_suffix)-1, 
                                  self.clique_dimension-1),
                        backtracked_state))

        while candidate_list:
            current_candidate = candidate_list.pop(0)
            if current_candidate in finished_words:
                continue

            length_difference = len(horocyclic_suffix) - len(current_candidate)

            if length_difference % 2:
                # `horocyclic_suffix` and `current_candidate` should
                # have opposite modes.
                if horocyclic_suffix.mode:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0]]\
                        + horocyclic_suffix[2] + [self.ray[1]]\
                        + horocyclic_suffix[3]
                    current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]+ [self.ray[0]]\
                        + self.extension_list[1][0:length_difference:]\
                        + current_candidate[2] + [self.ray[0]]\
                        + current_candidate[3]
                else:
                # In this case, `horocyclic_suffix` is 1 letter longer
                # than `current_candidate`, so to equalize the lengths,
                # two extra prefix letters are needed in
                # `current_candidate_equivalent`.
                    horocyclic_suffix_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1]\
                        + [self.ray[0] , self.ray[1]] + horocyclic_suffix[2]\
                        + [self.ray[0]] + horocyclic_suffix[3]
                    current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]\
                        + [self.ray[0], self.ray[1]]\
                        + self.extension_list[0][0:length_difference:]\
                        + current_candidate[2] + [self.ray[1]]\
                        + current_candidate[3]
            else:
                # `horocyclic_suffix` and `current_candidate` have the
                # same modes.
                if horocyclic_suffix.mode:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0]]\
                        + horocyclic_suffix[2] + [self.ray[1]]\
                        + horocyclic_suffix[3]
                    current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]+ [self.ray[0]]\
                        + self.extension_list[1][0:length_difference:]\
                        + current_candidate[2] + [self.ray[1]]\
                        + current_candidate[3]
                else:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0]\
                        + [self.ray[1]] + horocyclic_suffix[1]\
                        + [self.ray[0] , self.ray[1]] + horocyclic_suffix[2]\
                        + [self.ray[0]] + horocyclic_suffix[3]
                    current_candidate_equivalent = current_candidate[0]\
                        + [self.ray[1]] + current_candidate[1]\
                        + [self.ray[0], self.ray[1]]\
                        + self.extension_list[0][0:length_difference:]\
                        + current_candidate[2] + [self.ray[0]]\
                        + current_candidate[3]

            input_list = list(zip(horocyclic_suffix_equivalent+['-'], 
                                  current_candidate_equivalent+['-']))

            (input_accepted, end_state) =\
                self.different_length_edge_checker.process(
                    input_list, check_epsilon_transitions = False)

            if not input_accepted:
                finished_words.append(current_candidate)
                continue

            # The same length edge checker only tells us that no 
            # non-cancelable pair has been created.
            # To check whether the two have close successors, we need to
            # check whether there is an infinite alternation of some 
            # pair of letters as described in Proposition 5.2.10.

            canceling_word = end_state.label()[4]

            # `canceling_word` will be written after either 
            # `horocyclic_suffix` or `candidate_word`, depending on 
            # which word the cancelable letters belong to.
            # However, some of the letters of the canceling_word may 
            # have been prefix letters, and if so, writing them does not
            # change the suffix.
            # Since we are keeping track of edges between suffixes, we
            # must first process canceling_word slightly.
            # Recall that if the final state has `True` in index 11, it 
            # means that the second input contains cancelable letters, 
            # including perhaps a prefix letter.
            # Note that the uncanceled letters between subwords 1 and 2 
            # will always be uncancelable no matter what. So if prefix 
            # letters can be canceled, they must appear at the beginning
            # of the cancelable word.
            '''
            if end_state.label()[11]:
                if horocyclic_suffix[3] == 0:
                    #In this case, every extra prefix letter will appear in the cancelable set, but we want to drop all of them.
                    canceling_word = canceling_word[len(horocyclic_suffix)-len(current_candidate)::]
                elif extension_list[int(current_candidate.mode)][0] in self.alphabet.intersection(*[self.fsm_gen.lesser_star[letter] for letter in horocyclic_suffix[3]]):
                    #In this case, there is 1 extra prefix letter.
                    canceling_word = canceling_word[1::]
                    
                #Otherwise, the extra prefix letter is in the uncancelable set, so there is no need to worry about it.
            '''

            # We need to calculate which letters can follow our two words and still remain shortlex. We could reconstitute the full words.
            # However, if the Busemann value is large, this will involve processing a large amount of extraneous data.
            # Therefore, we find related words whose shortlex state will be the same as those of our words.

            # We want a pair of words horocyclic_suffix_equivalent and current_candidate_equivalent such that:
            # 1. Both of them are shortlex and have shortlex states equal to those of the full words.
            # 2. current_candidate_equivalent has extra prefix letter compared to horocyclic_suffix_equivalent, matching the difference between current_candidate and horocyclic_suffix


            '''
            if horocyclic_suffix.mode:
                if not current_candidate.mode:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0] + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0]] + horocyclic_suffix[2] + [self.ray[1]] + horocyclic_suffix[3]
                else:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0] + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0]] + horocyclic_suffix[2] + [self.ray[1]] + horocyclic_suffix[3]
            else:
                if not current_candidate.mode:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0] + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0] , self.ray[1]] + horocyclic_suffix[2] + [self.ray[0]] + horocyclic_suffix[3]
                else:
                    horocyclic_suffix_equivalent = horocyclic_suffix[0] + [self.ray[1]] + horocyclic_suffix[1] + [self.ray[0] , self.ray[1]] + horocyclic_suffix[2] + [self.ray[0]] + horocyclic_suffix[3]

            if current_candidate.mode:
                current_candidate_equivalent = current_candidate[0] + [self.ray[1]] + current_candidate[1] + [self.ray[0]] + current_candidate[2] + [self.ray[1]] + current_candidate[3]
            else:
                current_candidate_equivalent = current_candidate[0] + [self.ray[1]] + current_candidate[1] + [self.ray[0] , self.ray[1]] + current_candidate[2] + [self.ray[0]] + current_candidate[3]
            '''

            if end_state.label()[11]:
                horocyclic_suffix_equivalent = horocyclic_suffix_equivalent\
                    + list(canceling_word)
            else:
                current_candidate_equivalent = current_candidate_equivalent\
                    + list(canceling_word)

            horocyclic_next_letters = self.alphabet.difference(
                set(self.shortlex_machine.process(
                    horocyclic_suffix_equivalent)[1].label()))
            candidate_next_letters = self.alphabet.difference(
                set(self.shortlex_machine.process(
                    current_candidate_equivalent)[1].label()))

            '''

            if horocyclic_suffix.mode:
                if end_state.label()[11]:
                    # print ('input pair ', horocyclic_suffix, ' and ', candidate_input, ' with canceling word ', canceling_word)
                    HorocyclicState = self.horocyclic_suffix_machine_1234.process(horocyclic_suffix.word_as_list + list(canceling_word), check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1234.next_letters(HorocyclicState)
                else:
                    HorocyclicState = self.horocyclic_suffix_machine_1234.process(horocyclic_suffix.word_as_list, check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1234.next_letters(HorocyclicState)
            else:
                if end_state.label()[11]:
                    HorocyclicState = self.horocyclic_suffix_machine_1256.process(horocyclic_suffix.word_as_list + list(canceling_word), check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1256.next_letters(HorocyclicState)
                else:
                    HorocyclicState = self.horocyclic_suffix_machine_1256.process(horocyclic_suffix.word_as_list, check_epsilon_transitions = False)[1]
                    HorocyclicNextLetters = self.horocyclic_suffix_machine_1256.next_letters(HorocyclicState)

            if current_candidate.mode:
                if end_state.label()[11]:
                    CandidateState = self.horocyclic_suffix_machine_1234.process(current_candidate.word_as_list, check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1234.next_letters(CandidateState)
                else:
                    CandidateState = self.horocyclic_suffix_machine_1234.process(current_candidate.word_as_list+ list(canceling_word), check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1234.next_letters(CandidateState)
            else:
                if end_state.label()[11]:
                    CandidateState = self.horocyclic_suffix_machine_1256.process(current_candidate.word_as_list, check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1256.next_letters(CandidateState)
                else:
                    CandidateState = self.horocyclic_suffix_machine_1256.process(current_candidate.word_as_list+ list(canceling_word), check_epsilon_transitions = False)[1]
                    CandidateNextLetters = self.horocyclic_suffix_machine_1256.next_letters(CandidateState)

            '''

            letters_commuting_with_clique = set(end_state.label()[9])

            # Check whether any of these letters is permitted by both 
            # the above states.
            for letter in letters_commuting_with_clique:
                # Check if there is another letter in the alphabet which
                # does not commute with the given letter.
                if letter in horocyclic_next_letters.intersection(
                    candidate_next_letters)\
                        and letters_commuting_with_clique.difference(
                            self.c_map[letter].union({letter})) != set():
                    adjacencies.append(current_candidate)
                    break
            finished_words.append(current_candidate)
                    
        return adjacencies
        
    def calculate_divergence_adjacencies(self, horocyclic_suffix:HorocyclicWord)\
        -> list:
        
        '''
        Use `calculate_same_length_divergence_adjacencies` and 
        `calculate_shorter_divergence_adjacencies` to find all adjacent
         words which are at most as long as suffix.

        :param horocyclic_suffix: A horocyclic suffix.
        :return: All adjacent suffixes at most as long as `suffix`.
        '''

        adjacencies = []
        
        adjacencies.extend(
            self.calculate_same_length_divergence_adjacencies(horocyclic_suffix))
        adjacencies.extend(
            self.calculate_shorter_divergence_adjacencies(horocyclic_suffix))
        
        return adjacencies

    def calculate_divergence_horosphere_edges(self, horocyclic_suffix_list: list)\
        -> list:

        '''
        Calculate the set of edges from entries of `suffix_list` to 
        shorter suffixes.

        :param horocyclic_suffix_list: A list of horocyclic suffixes.
        :return: A list of all pairs of horocyclic suffixes whose
         corresponding words have close successors for all time such 
         that the first is an entry of `horocyclic_suffix_list` and the 
         second is no longer than the first.
        '''

        edges = []

        for suffix in horocyclic_suffix_list:
            for newsuffix in self.calculate_divergence_adjacencies(suffix):
                edges.append( (str(suffix), str(newsuffix)))
        return(edges)
        
    def horosphere_as_networkx(self, length: int, busemann_value: int):

        '''
        Find the divergence graph on a the set of suffixes at most a
        certain length.

        :param length: The maximum length desired. Time complexity is 
         O(n log (n)) in this factor.
        :param busemann_value): The value of the Busemann function
         desired. Only its parity will matter.
        :return: A `Graph`.
        '''
        suffixes = self.get_all_length_n_horocyclic_suffixes(
            length, bool(busemann_value % 2))
        # print(f"Suffixes of length {length} calculated:\
        #       \n\t\t {len(suffixes)} words found")
        # print(suffixes)
        edges = self.calculate_divergence_horosphere_edges(suffixes)
        # print(f"Words processing completed:\
        #       \n\t\t {len(suffixes)} words processed")
        # print(edges)

        G = nx.Graph()
        G.add_edges_from(edges)
        # print(f"Length {length} Horosphere generated: \n\t\t {G}")
        return G

    def _backtracking_recursive(self, word:HorocyclicWord, 
                                step_count:int, shortlex_state:FSMState) -> list:
        '''
        Recursively find all horocyclic suffixes `word` so that, as
         geodesic words, `word`=`word' + tail`, where `tail` is a 
         shortlex word `step_count` letters long.
         The assumption that tail is shortlex is only relevant to make
         the outputs unique.

        :param word: the word that has been reached so far.
        :param step_count: the number of steps to be backtracked.
        :param shortlex_state: the shortlex state of `word`.
        :return: a list without repetition of the word `word` as above.
        '''

        if step_count == 0:
            return([word])

        resulting_words = []

        # We backtrack by the letters that are both final letters of
        # `word` and still allowed by the shortlex state.
        last_letters = set(self.geodesic_machine.process(word.word_as_list)\
            [1].label())
        for transition in self.shortlex_machine.transitions(shortlex_state):
            # Recall that transition.word_in outputs a list containing 
            # the label of the transition, not the label itself. 
            if transition.word_in[0] in last_letters:
                for i in reversed(range(0,4)):
                    if transition.word_in[0] in set(word[i]):
                        new_subword_list = copy.deepcopy(word.subword_list)
                        reversed_subword = copy.deepcopy(word[i])[::-1]
                        deletion_index = reversed_subword.index(
                            transition.word_in[0])
                        deleted_subword = (reversed_subword[0:deletion_index:] +\
                                           reversed_subword[deletion_index+1::])\
                                            [::-1]
                        new_subword_list[i] = deleted_subword
                        new_word = self.word_gen.horocyclic_word(
                            new_subword_list, word.mode)
                        break
                resulting_words.extend(self._backtracking_recursive(
                    new_word, step_count-1, transition.to_state))
        return resulting_words

    def _geodesic_successor_horocyclic_suffixes(self, word:HorocyclicWord,
                                                step_count:int,
                                                geodesic_suffix_state:FSMState
                                                ) -> list:

        '''
        Recursively find all horocyclic suffixes `word'` that are 
        `step_count` letters longer than `word`, such that `word'` is a
        geodesic successor to `word`.

        :param word: The word to find successors to.
        :param step_count: the number of letters to write after `word`.
        :param geodesic_suffix_state: the state of `word` in the 
         geodesic suffix machine.
        :return: a list with repetition of all words `word'` as above.
        '''
        
        if step_count == 0:
            return [word]
        
        if step_count < 0:
            raise ValueError('Cannot go a negative number of steps forward.\
                Use the `_backtracking_recursive` function to go backwards.')
        
        resulting_words = []  
        
        for transition in self.geodesic_suffix_machine.transitions(
            geodesic_suffix_state):
            # Determine which subword `transition.word_in` should be 
            # inserted into. Recall that `transition.word_in` is a 
            # singleton list.
            if word.mode:
                earliest_possible_subword = self.subword_dict_1234[
                    transition.word_in[0]]
            else:
                earliest_possible_subword = self.subword_dict_1256[
                    transition.word_in[0]]
            
            for i in reversed(range(earliest_possible_subword-1,4)):
                # `transition.word_in` belongs in subword i either if it
                # cannot commute to an earlier subword, or if subword i 
                # is the earliest subword the letter is allowed in.
                if (i == earliest_possible_subword-1 or
                    (not self.fsm_gen._test_set_pair_commutation(
                        {transition.word_in[0]},set(word[i])))):
                    new_subword_list = copy.deepcopy(word.subword_list)
                    new_subword = self.word_gen.word(word[i])
                    # Recall that transition.word_in is a singleton list.
                    new_subword.shortlex_append(transition.word_in[0])
                    new_subword_list[i] = new_subword.word_as_list
                    new_word = self.word_gen.horocyclic_word(
                        new_subword_list, word.mode)
                    break
            resulting_words.extend(self._geodesic_successor_horocyclic_suffixes(
                new_word, step_count-1, transition.to_state))
            
        return resulting_words

    def _switch_form_special_case(self, word:HorocyclicWord) -> HorocyclicWord:

        '''
        Given a horocyclic suffix of form 1234, return an equal 
        horocyclic suffix of form 1256, or vice versa.
        
        Only implemented in the case that subword 3 is empty and that
        subword 4 consists of letters commuting with the ray letter that
        is between word_5 and word_6 if word is of form 1234,
        or vice versa.
      
        :param word: A `HorocyclicWord` with empty third subword and
         subword 4 satisfying the condition above.
        :return: An equivalent `HorocyclicWord` of the opposite form to 
         that of `word`.
        '''
    
        if word[2] != []:
            raise ValueError('Not implemented in the general case')
    
        # With this assumption, once a letter of word[4] is read that 
        # follows this ray letter, no letter preceding the ray letter 
        # can be written until a letter is written that does not commute
        # with it. Therefore, the first time a letter of word[4] follows
        # the relevant ray letter is the break between the resulting 
        # subwords. This takes linear time to compute. Without the 
        # assumption, it would take quadratic time.

        # We will need to insert a letter into the fourth subword of 
        # `word`. If `word` is of the form 1234, then the letter to be
        # inserted is `self.ray[0]`, and vice versa.
        split_letter = self.ray[1-int(word.mode)]
        
        #sentinel value
        split_index = None
        
        for index in  range(0, len(word[3])):
            if not word[3][index] in self.c_map[split_letter]:
                raise ValueError('Not implemented in the general case')
            if (self.o_map[word[3][index]] > self.o_map[split_letter] and
              split_index is None):
                split_index = index
                
        # At the end of either loop, `split_index` records either the 
        # first instance of a letter commuting with and following 
        # `split_letter`, or, if each letter commutes with and precedes
        # `split_letter`, then `split_index` still has the sentinel 
        # value `None`.
        if split_index is None:
            new_word = self.word_gen.horocyclic_word(
                [word[0], word[1], word[3],[]], not word.mode)
        else:
            new_word = self.word_gen.horocyclic_word(
                [word[0], word[1], word[3][:split_index:], 
                 word[3][split_index::]], not word.mode)
    
        return new_word
    
    #Not used in the below.

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
    
