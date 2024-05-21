from sage.combinat.finite_state_machine import FSMState, Automaton
from itertools import product
import copy
from enhanced_automaton import EnhancedAutomaton
from rips_fsm_generator import RipsFSMGenerator
from words import WordGenerator

class DivergenceFSMGenerator(RipsFSMGenerator):


    def __init__(self, commutation_dict:dict[str, set],
                 order_dict: dict[str, int], ray: tuple[str]):
        
        '''
        This object will make the necessary automata for computing the
         Divergence Graph. 
    
        :param commutation_dict: A dictionary representation of a 
         defining graph. A keys are labels of vertices, and values are
         the set of adjacent vertices. This list should not include the
         key letter. In the RACG, `letter` commutes with itself and with
         `self.commutation_dict[letter]`

        :param order_dict: A dictionary representation of a total 
         ordering on the alphabet. All values should be distinct.
        
        :param ray: A list of two characters that will be used to 
         generate the chosen ray to infinity. In the paper these are 
         referred to as a_i and a_j respectively.
        '''

        if not len(ray) == 2:
            raise ValueError ("The defining ray should have two letters")
        elif ray [1] in commutation_dict[ray[0]]:
            raise ValueError ("The defining ray consists of two letters\
                              which commute")
        
        if len(order_dict.values()) != len(set(order_dict.values())):
            raise ValueError ('The provided order is not a total order')
        
        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray

        for letter in self.alphabet:
            for adjacent_letter in self.c_map[letter]:
                if not letter in self.c_map[adjacent_letter]:
                    raise ValueError('Parameter commutation_dict is not\
                                     symmetric')

        self.word_generator_machine = WordGenerator(self.c_map, self.o_map)
        
        string_of_all_letters = ''.join(letter for letter in self.alphabet)
        if '-' in string_of_all_letters:
            raise ValueError ('''The character '-'
                               is reserved to be the blank character''')
        if ',' in string_of_all_letters:
            raise ValueError('''The character ','
                              is reserved for delimiting lists''')
        
        # The lesser_star dictionary agrees with the function Star_< in 
        # the paper. When passed a key of a letter, it returns the set 
        # of letters that commute with and precede the key. 
        # Note the strict inequality.
        self.lesser_star = {}
        for letter in self.alphabet:
            self.lesser_star[letter] = set(
                filter(lambda x: self.o_map[x] < self.o_map[letter],
                       self.c_map[letter])
        )
        self.greater_star = {}
        for letter in self.alphabet:
            self.greater_star[letter] = self.c_map[letter].difference(
                self.lesser_star[letter])
            
    def horocyclic_suffix_machine_1(self) -> EnhancedAutomaton:
        
        '''
        Generate the w_1 machine.

        This machine accepts words spelled in the letters that 
         commute with both letters of the ray and precede the second
         one (a_j).
        '''

        w1_machine = self.shortlex_machine(
            self.c_map[self.ray[0]].intersection(self.lesser_star[self.ray[1]]))

        return w1_machine

    def horocyclic_suffix_machine_2(self) -> EnhancedAutomaton:
        
        '''
        Generate the w_2 machine. 
        This machine accepts words spelled in the letters that 
        commute with both letters of the ray, precede the first one 
        (a_i), and follow the second one (a_j).
        '''
        
        w2_machine = self.shortlex_machine(
            self.lesser_star[self.ray[0]]\
                .intersection(self.greater_star[self.ray[1]]))

        return w2_machine

    
    def horocyclic_suffix_machine_1234(self) -> EnhancedAutomaton:

        '''
        Generate an FSM which accepts one of the two horocyclically
         shortlex word forms.

        :return: an Automaton whose accepted language is the set of 
         words w_1w_2w_3w_4 as described in the paper.
        ''' 

        # w_3w_4 is a concattenation of shortlex words such that:
        # 1. w_3 is spelled with letters commuting with and preceding 
        #    a_j, and cannot be made to begin with a letter commuting
        #    a_i.
        # 2. w_4 cannot be made to begin with a_j, or a letter
        #    commuting with and preceding a_j.
        # 3. w_3w_4, as a whole, cannot be rearranged to begin with a
        #    letter commuting with both letters and preceding a_i, or
        #    to begin with a_i.

        w3_machine = self.shortlex_machine(
            self.lesser_star[self.ray[1]]).enhanced_intersection(
                self.first_letter_excluder(self.c_map[self.ray[0]]))

        # This machine is so-named because its language is not exactly 
        # the words w_4, since in fact whether a word is allowed to be
        # w_4 depends on w_3 by condition 3 above.
        w4_machine_approx = self.shortlex_machine()\
            .enhanced_intersection(self.first_letter_excluder(
                self.lesser_star[self.ray[1]].union({self.ray[1]}))
            )
        
        w1_machine = self.horocyclic_suffix_machine_1()
        w2_machine = self.horocyclic_suffix_machine_2()
        w12_machine = w1_machine.unambiguous_concatenation(w2_machine)
        
        restricted_alphabet = {self.ray[0]}.union(
            self.lesser_star[self.ray[0]].intersection(self.c_map[self.ray[1]]))

        w34_machine = (w3_machine.unambiguous_concatenation(w4_machine_approx))\
            .enhanced_intersection(self.first_letter_excluder(restricted_alphabet))

        return w12_machine.unambiguous_concatenation(w34_machine)

    def horocyclic_suffix_machine_1256(self) -> EnhancedAutomaton:
  
        '''
        Generate an FSM which accepts one of the two horocyclically
         shortlex word forms.

        :return: an Automaton whose accepted language is the set of 
         words w_1w_2w_5w_6 as described in the paper.
        ''' 

        #w_5w_6 is a concattenation of shortlex words such that:
        # 1. w_5 is spelled with letters commuting with and preceding
        #    a_i, and cannot be made to begin with a letter commuting
        #    a_j.
        # 2. w_6 cannot be made to begin with a_i, or a letter 
        #    commuting with and preceding a_i.
        # 3. w_5w_6, as a whole, cannot be rearranged to begin with a
        #    letter commuting with both a_i and a_j and preceding a_j,
        #    or to begin with a_j.
        
        w5_machine = self.shortlex_machine(
            self.lesser_star[self.ray[0]]).enhanced_intersection(
                self.first_letter_excluder(self.c_map[self.ray[1]]))

        #This machine is so-named because its language is not exactly 
        # the words w_6, since in fact whether a word is allowed to be
        # w_6 depends on w_5 by condition 3 above.
        w6_machine_approx = self.shortlex_machine()\
        .enhanced_intersection(self.first_letter_excluder(
            self.lesser_star[self.ray[0]].union({self.ray[0]}))
            )

        w1_machine = self.horocyclic_suffix_machine_1()
        w2_machine = self.horocyclic_suffix_machine_2()
        w12_machine = w1_machine.unambiguous_concatenation(w2_machine)
        
        restricted_alphabet = {self.ray[1]}.union(
            self.lesser_star[self.ray[1]].intersection(self.c_map[self.ray[0]]))
        w56_machine = (w5_machine.unambiguous_concatenation(w6_machine_approx))\
            .enhanced_intersection(self.first_letter_excluder(restricted_alphabet))

        return w12_machine.unambiguous_concatenation(w56_machine)

    #We will not use the even_horocyclic_suffix_machine or the
    # odd_horocyclic_suffix_machine in practice.
    
    def even_horocyclic_suffix_machine(self) -> EnhancedAutomaton:

        return ((self.horocyclic_suffix_machine_1256())._interspersal(
            self.horocyclic_suffix_machine_1234()))

    def odd_horocyclic_suffix_machine(self) -> EnhancedAutomaton:

        return ((self.horocyclic_suffix_machine_1234())._interspersal(
            self.horocyclic_suffix_machine_1256()))

    def horocyclic_edge_checker(self, subword_dict) -> Automaton:

        '''
        Generate the machine that checks for noncommuting uncancellable 
        pairs between a pair of words. 
        
        The inputs will be pairs (w_letter,v_letter) or the pair 
        ('-','-'). The latter denotes the end of the word.

        The `subroutines generate_states_without_uncancelables`,
         `generate_first_noncanceling_transitions`, 
         `get_nonterminal_transitions`, and `get_double_blank_transition`
         will all be defined later.
        
        :param subword_dict: A dictionary that keeps track of which 
         letters first appear in which subword. It will have values 1-4
         if the two words are of the same length and values 1-3 if the 
         two are of different lengths. This is because in the case that 
         `w_suff` is 1 letter shorter than `v_suff`, we will compare
         `w_1w_2w_3self.ray[1]w_4-` with `v_1v_2 v_6-`, or
         `w_1w_2w_5self.ray[0]w_6-` with `v_1v_2 v_4-`.
        In the first case, letters of `w_3self.ray[1]w_4` can cancel 
         with those of `v_6`, while in the second case, letters of 
         `w_5self.ray[0]w_6` can cancel with those of `v_4`.
        
        :return: an Automaton which accepts as inputs pairs of letters,
         one from `w` and one from `v`, such that the words such that 
         the lengths of each word are equal and there is no uncancelable
         pair
        '''        

        non_final_states = []
        final_states = []
        total_transitions = []
        finished_states = []

        final_subword = max(subword_dict.values())

        # First, we generate those states that have no uncancelable 
        # letters.
        (states_without_uncancelables, new_transitions) = \
            self.generate_states_without_uncancelables(subword_dict)

        # print('Completed the uncancelable states. There are ', len(states_without_uncancelables), ' of them.')
        
        non_final_states.extend(states_without_uncancelables)
        total_transitions.extend(new_transitions)
        
        #Then, we generate their immediate successors.
        for state_without_uncancelables in states_without_uncancelables:
            (new_states, new_transitions) = \
                self.generate_first_noncanceling_transitions(
                    state_without_uncancelables,subword_dict)
            non_final_states.extend(new_states)
            total_transitions.extend(new_transitions)
            finished_states.append(state_without_uncancelables)

        # print('Completed the first batch of transitions. There are ', len(total_transitions), 'transitions and ', len(set(non_final_states)), ' states in total')
        
        #Run a BFS to find the remaining non-final states.
        while non_final_states:
            source_state = non_final_states.pop(0)
            if source_state in finished_states:
                continue

            (new_states, new_transitions) = \
                self.get_nonterminal_transitions(
                    source_state, subword_dict)
            non_final_states.extend(new_states)
            total_transitions.extend(new_transitions)
            finished_states.append(source_state)

        # print('Completed the nonterminal transitions. There are ', len(total_transitions), ' transitions and ', len(set(finished_states)), ' states in total')
        
        #Finally, we add transitions processing the `('-','-')` input.
        for source_state in finished_states:
            try:
                (final_state, final_transition) = \
                    self.get_double_blank_transition(
                        source_state, final_subword)
            except TypeError:
                continue
            final_states.append(final_state)
            total_transitions.append(final_transition)

        # print('completed the final transitions. There are ', len(total_transitions), 'transitions and ', len(set(final_states)), ' final states in total')
        
        initial_state_label = ( (), (), (),  (), (), (), (), (), (),
                                tuple(self.alphabet), (1, 1), True )
        return Automaton(total_transitions, [initial_state_label], final_states)
    
    # What follow are subroutines for the method 
    # `horocyclic_edge_checker_same_length`. 
    #
    # To improve performance and make certain features of
    # sage.combinat.finite_state_machine usable, the state labels must
    # be hashable, but to make changes, we will want mutable types.
    #
    # The following describes the state labels.
    # 4 entries for the subwords u_j (j=1, 2, 3, 4) of potentially 
    #  cancelable letters. These will be tuples (hashable) or instances 
    #  of the Word Class (mutable).
    # 4 entries for the geodesic first letters of each of the u_j, and
    #  of each of their truncations. These will be tuples of pairs of 
    #  tuples (hashable) or lists of pairs of sets (mutable).
    #  This will be formatted as a tuple or list of pairs (first letters,
    # potential first letters).
    # These first 8 entries will alternate, so that the data for the 
    # subword u_j appears at indices 2*j-2 and 2*j-1.
    # 1 entry for the uncancelable letters, in a tuple (hashable) or 
    # set (mutable).
    # 1 entry for the letters that commute with each uncancelable
    # letter, in a tuple (hashable) or set (mutable).
    # 1 tuple of 2 integers n_w and n_v keeping track of which subword 
    # the two inputs are on.
    # 1 bit. True will mean that the second input (v) is the one which 
    # contains the potentially cancelable letters. False will mean that
    # the first input (w) contains the potentially cancelable letters.
    # Its initial value is arbitrarily set to True.
    # All of the above data will be placed into a tuple (hashable)
    # or list (mutable).
    #
    # The two inputs are the 'adding input' (the word that has the 
    # cancelable letters) and the 'canceling input'. So the bit True
    # means that v is adding and w is canceling.
    
    
    def generate_states_without_uncancelables(self, subword_dict:dict[str: int])\
          -> tuple:
        
        '''
        Generate the states of the machine which do not record any
        uncancelable letters, as well as the transitions between them.

        :param subword_dict: A dictionary whose keys are letters and
         whose values are the first subword that letter appears in.
        :return: A pair consisting of a list of state labels without 
         uncancelable letters, and a list of the transitions between 
         them.
        '''
        
        transition_list = []
        states_without_uncancelables = []

        # This state will always exist
        initial_state =  ((), (), (),  (), (), (), (), (), (),
                          tuple(self.alphabet), (1, 1), True)

        states_without_uncancelables.append(initial_state)

        # We only need a state without uncancelables for each subword
        # that will actually appear.
        for value in set(subword_dict.values()).difference({1}):
            new_state =  ((), (), (),  (), (), (), (), (), (), 
                          tuple(self.alphabet), (value, value), True) 
            states_without_uncancelables.append(new_state)
               
        for source_state in states_without_uncancelables:
            for letter in self.alphabet:
                new_subword = max(source_state[10][0], subword_dict[letter])
                new_state = ((), (), (),  (), (), (), (), (), (), 
                             tuple(self.alphabet), (new_subword, new_subword),
                             True) 
                transition_list.append(
                    (source_state, new_state, (letter, letter)))

        return (states_without_uncancelables, transition_list)

    def generate_first_noncanceling_transitions(self, state_without_uncancelables:tuple,\
                                                 subword_dict:dict[str: int]) -> tuple:
        
        '''
        Generate the first states of the machine that record only a
         single uncancelable letter which follow a specific state
         without uncancelables.

        :param state_without_uncancelables: The label of a state that
         records no uncelable letters. 
        :param subword_dict: A dictionary whose keys are letters and
         whose values are the first subword that letter appears in.
        :return: A pair consisting of a list of state labels with a 
         single uncancelable letter, and a list of the transitions 
         from `state_without_uncancelables` to them.
        '''

        if state_without_uncancelables[8] != ():
            raise ValueError('This state has uncancelable letters')
        
        resulting_states = []
        transitions = []
        
        for letter_pair in product(self.alphabet, self.alphabet):
            w_letter = letter_pair [0]
            v_letter = letter_pair [1]
            # We can assume the two commute, or else we immediately 
            # reach a failure state.
            if w_letter not in self.c_map[v_letter]:
                # This includes the case that `w_letter == v_letter`.
                continue
 
            new_label = self._mutable_label(state_without_uncancelables)
            new_n_w = max(new_label[10][0], subword_dict[w_letter])                    
            new_n_v = max(new_label[10][1], subword_dict[v_letter])
            new_label[10] = (new_n_w, new_n_v)
            # We compute the next value of the bit. True means that the 
            # v is the adding word and False means that w is the adding
            # word.
            new_bit = ((new_n_w < new_n_v) or
                       (new_n_w == new_n_v\
                        and self.o_map[w_letter] < self.o_map[v_letter])
                       )
            new_label[11] = new_bit
            adding_letter = letter_pair[int(new_bit)]
            adding_subword = new_label[10][int(new_bit)]
            canceling_letter = letter_pair[1-int(new_bit)]
            
            # Add the `adding_letter`.
            new_label[2*adding_subword -2].append(adding_letter)
            # The `adding_letter` is the first letter of the relevant 
            # word. The other possible first letters are those that 
            # commute with it.
            new_label[2*adding_subword -1].append(({adding_letter},
                                                   self.c_map[adding_letter]))
            
            # Since the `adding_letter` and the `canceling_letter` do 
            # not equate, there is no need to check for cancelation.
            # `canceling_letter` automatically becomes uncancelable.
            new_label[8] = {canceling_letter}
            new_label[9].intersection_update(self.c_map[canceling_letter])
            
            new_state = self._hashable_label(new_label)
            resulting_states.append(new_state)
            new_transition = (state_without_uncancelables, new_state,
                              letter_pair)
            transitions.append(new_transition)

        return((resulting_states, transitions))

    def get_nonterminal_transitions(self, source_state, 
                                    subword_dict: dict[str: int]) -> tuple:
        
        '''
        Generate the nonterminal successors of a state that has some
         uncancelable letters.
        
        :param source_state: An FSMState with some uncancelable letters. 
        :param subword_dict: A dictionary whose keys are letters and 
         whose values are the first subword that letter appears in.
        :return: A pair consisting of a list of the states that follow 
         source_state and a list a of the transitions out of source_state.
        '''

        old_bit = source_state[11]

        resulting_states = []
        transitions = []

        for letter_pair in product(source_state[9], source_state[9]):
            w_letter = letter_pair [0]
            v_letter = letter_pair [1]
            adding_letter = letter_pair[int(old_bit)]
            canceling_letter = letter_pair[1-int(old_bit)]
            
            new_label = self._mutable_label(source_state)
            new_n_w = max(new_label[10][0], subword_dict[w_letter])                    
            new_n_v = max(new_label[10][1], subword_dict[v_letter])
            new_subword_pair = (new_n_w, new_n_v)
            adding_subword = new_subword_pair[int(old_bit)]
            canceling_subword = new_subword_pair[1-int(old_bit)]
            new_label[10] = new_subword_pair

            # Append the new letter to the relevant subword.
            new_label[2*adding_subword-2].append(adding_letter)
            # Update the first letters.
            for first_letters_set in new_label[2*adding_subword-1]:
                if adding_letter in first_letters_set[1]:
                    first_letters_set[0].add(adding_letter)
                first_letters_set[1].intersection_update(
                    self.c_map[adding_letter])
            new_label[2*adding_subword-1].append(
                ({adding_letter},self.c_map[adding_letter]))

            # Compute the next bit value.
            present_letter_list = new_label[0].word_as_list\
                + new_label[2].word_as_list + new_label[4].word_as_list\
                + new_label[6].word_as_list
            present_letters = set(present_letter_list)
            # Check whether the bit value needs to be flipped.
            letters_following_present_letters = copy.copy(self.alphabet)
            for letter in present_letters:
                letters_following_present_letters.intersection_update(
                    self.greater_star[letter])
            bit_flip = ((canceling_subword > adding_subword) or \
                       ((canceling_subword == adding_subword) \
                        and canceling_letter in letters_following_present_letters)
                        )
            # `exor True`` is the same as `not`, while `exor False` 
            # does nothing.
            new_label[11] = old_bit ^ bit_flip

            if bit_flip:
                # Every previously cancelable letter will become 
                # uncancelable. 
                # This will create an uncancelable pair if any of them
                # fail to cancel with one another or with 
                # `canceling_letter`.
                #
                # We also check whether there are any duplicates among 
                # among the present letters.
                #
                # It is not possible for `canceling_letter` to be in 
                # `present_letters` in this case, so we need not check
                # for disjointness.
                if (len(present_letter_list) > len(present_letters)) or\
                    (not (self._test_set_commutation(present_letters) and\
                          self._test_set_pair_commutation(
                              {canceling_letter},present_letters)
                    )):
                    continue
                                
                # Add every remaining cancelable letter into the
                # uncancelable set.
                new_label[8] = new_label[8].union(present_letters)
                for letter in present_letters:
                    new_label[9].intersection_update(self.c_map[letter])
            
                # Delete every previously cancelable letter, and 
                # initialize a new single cancelable letter.
                # Because we have just flipped the bit, the new 
                # `canceling_subword` and new `canceling_letter` 
                # take the place that the new `adding_subword` and 
                # `adding_letter` had.
                for i in range(0,4):
                    new_label[2*i] = self.word_generator_machine.word([])
                    new_label[2*i+1] = []
                new_label[2*canceling_subword-2] = \
                    self.word_generator_machine.word(canceling_letter)
                new_label[2*canceling_subword-1].append(
                    ({canceling_letter}, self.c_map[canceling_letter]))
                new_state = self._hashable_label(new_label)
                resulting_states.append(new_state)
                new_transition = (source_state, new_state, letter_pair)
                transitions.append(new_transition)
                continue

            # Since the bit has not flipped, we just need to process
            # `canceling_letter`.
            new_label = self.process_canceling_letter(
                new_label, canceling_letter)
            # If this created an uncancelable pair, then continue.
            if new_label is None:
                continue
            new_state = self._hashable_label(new_label)
            resulting_states.append(new_state)
            new_transition = (source_state, new_state, (w_letter, v_letter))
            transitions.append(new_transition)

        return (resulting_states, transitions)

    def process_canceling_letter(self, label:list, canceling_letter:str)-> list:
        
        '''
        Take the mutable label of a state to which the adding letter has
         already been added and for which the bit has not flipped, and
         evaluate whether `canceling_letter` cancels.

        
        :param label: the mutable label of a state as above.
        :param canceling_letter: the letter whose cancelation is to be 
         tested.
        :return: The mutable label of the resulting state, or None if 
         processing `canceling_letter` creates an uncancelable pair.
        '''

        canceling_subword = label[10][1-int(label[11])]
        new_uncancelable_list = []
        # If a new subword has started, then the remaining letters from 
        # the previous subword(s) become uncancellable.
        for i in range (0, canceling_subword-1):
            new_uncancelable_list.extend(label[2*i].word_as_list)
            label[2*i] = self.word_generator_machine.word([])
            label[2*i+1] = []
        new_uncancelables = set(new_uncancelable_list)
        # This will create an uncancellable pair if any of the newly
        # uncancelable letters fail to commute with one another, or any
        # of them fail to commute with a remaining letter, or if they 
        # don't commute with the `canceling_letter`.
        # Since there may be more new_uncancelables after checking 
        # whether the `canceling_letter` cancels all we must check now is
        # whether the `canceling_letter` commutes to the matching
        # `adding_subword`. 
        # It is not possible for `canceling_letter` to be in 
        # `new_uncancelables` because then `canceling_letter` would have
        # to have appeared in `adding_subword` earlier than possible. 
        # So there is not need to ask for disjointness.
        if not self._test_set_pair_commutation({canceling_letter}, 
                                               new_uncancelables):
            return None

        # Now we check whether the `canceling_letter` actually cancels.
        # This idiom avoids problems with indexing into empty lists.
        if canceling_letter in next(iter(label[2*canceling_subword-1]),
                                    (set(), set()))[0]:
            canceling_index = label[2*canceling_subword-2].index(
                canceling_letter)
            # These letters have just become uncancellable.
            new_uncancelable_list.extend(label[2*canceling_subword-2]\
                                         [:canceling_index])
            # This is the remaining potentially cancelable word.
            label[2*canceling_subword-2] = self.word_generator_machine.word(
                label[2*canceling_subword-2][canceling_index+1:])
            label[2*canceling_subword-1] = label[2*canceling_subword-1]\
                [canceling_index+1:]
            # Update which letters are present.
            remaining_letters = set(label[0].word_as_list).union(
                set(label[2].word_as_list), set(label[4].word_as_list), 
                set(label[6].word_as_list))
            # Check whether there are duplicate uncancellable letters.
            new_uncancelables = set(new_uncancelable_list)
            if len(new_uncancelable_list) > len(new_uncancelables):
                return None
            # Check whether there is an uncancellable pair, either 
            # between the new uncancelables or with the remaining 
            # letters. In this case we will demand disjointness.
            if not (self._test_set_pair_commutation(
                new_uncancelables, remaining_letters, all_distinct=True) 
                and self._test_set_commutation(new_uncancelables)):
                return None
            # If there are no uncancelable pairs, then we get a new 
            # transition. We will update the uncancelable set and the 
            # set of accepted next letters outside the if statement.
            for letter in new_uncancelables:
                label[8].add(letter)
                label[9].intersection_update(self.c_map[letter])
            return label
        else:
            # If the canceling_letter does not cancel, then it joins the
            # uncancelable set.
            new_uncancelable_list.append(canceling_letter)
            # Additionally, any cancelable letters commuting to the 
            # start of the canceling word, and commuting with and 
            # preceding `canceling_letter` become uncancelable.
            if label[2*canceling_subword-1]:
                truncation_index = max((label[2*canceling_subword-2].index(letter)\
                                        for letter in self.lesser_star[
                                            canceling_letter].intersection(
                                            label[2*canceling_subword-1][0][0])),
                                        default=None)
                if truncation_index is not None:
                    # These letters become uncancelable. 
                    # It is possible that some letters that precede
                    # `truncation_index` do not commute with and precede
                    # `canceling_letter`. However, this can only happen
                    # if we have created an uncancelable pair. So it
                    # does not matter that we mark (incorrectly) as
                    # uncancelable here, since the subroutine will
                    # terminate by returning `None` regardless.
                    new_uncancelable_list.extend(label[2*canceling_subword-2]\
                                            [:truncation_index+1])
                    # This is the remaining potentially cancelable word.
                    label[2*canceling_subword-2] = self.word_generator_machine.word(
                        label[2*canceling_subword-2][truncation_index+1:])
                    label[2*canceling_subword-1] = label[2*canceling_subword-1]\
                        [truncation_index+1:]
                
            # Update which letters are present.
            remaining_letters = set(label[0].word_as_list).union(
                set(label[2].word_as_list), set(label[4].word_as_list), 
                set(label[6].word_as_list))
            # Check whether there are duplicate uncancellable letters.
            new_uncancelables = set(new_uncancelable_list)
            if len(new_uncancelable_list) > len(new_uncancelables):
                return None
            # Check whether there is an uncancellable pair, either 
            # between the new uncancelables or with the remaining 
            # letters. In this case we will demand disjointness.
            if not (self._test_set_pair_commutation(
                new_uncancelables, remaining_letters, all_distinct=True) 
                and self._test_set_commutation(new_uncancelables)):
                return None
            # If there are no uncancelable pairs, then we get a new transition.
            for letter in new_uncancelables:
                label[8].add(letter)
                label[9].intersection_update(self.c_map[letter])
            return label
    
    def get_double_blank_transition(self, source_state, final_subword:int)->tuple:
        
        '''
        This method takes any nonterminal source_state and computes the
        outgoing transition labeled ('-', '-').
        :param source_state: The label of a non-final state.
        :param final_subword: 3 or 4, depending on the number of 
        different values of `subword_dict`.
        :return: A pair consisting the label of a final state and the
         defining data of a transition from `source_state` to this final
         state labeled `('-', '-')`. If ending the inputs here yields an
         uncancelable pair, then `None` is returned instead.
        '''

        new_label = self._mutable_label(source_state)
        new_uncancelable_list = []
        
        # All subwords but the final one have ended, so no more
        # cancelation is possible for them.
        for i in range (1, final_subword):
            new_uncancelable_list.extend(new_label[2*i-2].word_as_list)
            new_label[2*i-2] = self.word_generator_machine.word([])
            new_label[2*i-1] = []
        present_letters = set(new_label[2*final_subword - 2].word_as_list)
        new_uncancelables = set(new_uncancelable_list)
        # Check whether we have created an uncancelable pair.
        if len(new_uncancelable_list) > len(new_uncancelables):
            return(None)
        if not (self._test_set_commutation(new_uncancelables) \
                and self._test_set_pair_commutation(
                    new_uncancelables, present_letters, True)):
            return(None)
        
        # Since we have not created an uncancelable pair, we get a valid
        # transition.
        for letter in new_uncancelables:
            new_label[8].add(letter)
            new_label[9].intersection_update(self.c_map[letter])
        new_label[10] = (final_subword, final_subword)
        
        # Avoid states that have matching labels.
        new_label.append('final')
        
        new_state = self._hashable_label(new_label)
        return(new_state, (source_state, new_state, ('-','-')))

    def _mutable_label(self, hashable_label:tuple) -> list:

        '''Take the hashable form of a label and render it mutable.'''
    
        mutable_label = list(hashable_label)
        
        for i in range (0, 4):
            mutable_label[2*i] = self.word_generator_machine.word(
                hashable_label[2*i])
            new_list = []
            for (first_letter_tuple, potential_first_letter_tuple) in \
              hashable_label[2*i+1]:
                new_list.append((set(first_letter_tuple),
                                 set(potential_first_letter_tuple)))
            mutable_label[2*i+1] = new_list
        mutable_label[8] = set(hashable_label[8])
        mutable_label[9] = set(hashable_label[9])
        
        return(mutable_label)
    
    def _hashable_label(self, mutable_label:list) -> tuple:
        
        '''Take the mutable form of a label and render it hashable.'''

        for i in range (0, 4):
            mutable_label[2*i] = mutable_label[2*i].word_as_tuple()
            new_list = []
            # Coerce the first letter data into tuples.
            for (first_letter_set, potential_first_letter_set) in\
              mutable_label[2*i+1]:
                new_list.append((tuple(sorted(first_letter_set, 
                                              key = lambda x: self.o_map[x])),
                                 tuple(sorted(potential_first_letter_set,
                                              key = lambda x: self.o_map[x]))
                                              ))
            mutable_label[2*i+1]=tuple(new_list)
        # Turn the sets of uncancelable and acceptable letters into
        # tuples.
        mutable_label[8] = tuple(sorted(mutable_label[8],
                                        key = lambda x: self.o_map[x]))
        mutable_label[9] = tuple(sorted(mutable_label[9],
                                        key = lambda x: self.o_map[x]))
    
        return(tuple(mutable_label))

    def _test_set_commutation(self, letter_set: set) -> bool:

        '''
        Take a set of input characters and check whether they pairwise 
        commute.

        :param letter_set: A subset of `self.alphabet`.
        '''

        letter_list = sorted(letter_set, key = lambda x: self.o_map[x])
        for i in range(0, len(letter_list)):
            # There is no need to include `letter_list[i]` in the set of
            # letters it commutes with, because letter_set is a set. We 
            # will never test its commutation against itself.
            ith_letter_neighbors = self.c_map[letter_list[i]]
            for j in range(i+1, len(letter_list)):
                if j not in ith_letter_neighbors:
                    return(False)
        return(True)

    def _test_set_pair_commutation(self, first_letter_set: set, 
                                   second_letter_set: set, all_distinct = False)\
                                   -> bool:
        
        '''
        Test whether each element of one set commutes with each element 
        of another. Optionally, also check that there are no elements
        in both sets.

        :param first_letter_set: One of two sets to test commutation of.
        :param second_letter_set: The second set to test commutation of.
        :param all_distinct: Whether to test that there is no overlap.
        
        :return: `False` if any element of `first_letter_set` fails to 
         commute with any letter of `second_letter_set`. Otherwise, 
         `False` if `all_distinct` is `True` and the two sets are not
         disjoing. Otherwise, `True`.
        '''
        
        if all_distinct and (first_letter_set.intersection(second_letter_set)\
                             != set()):
            return(False)
        for letter_pair in product(first_letter_set, second_letter_set):
            if not letter_pair[0] in (self.c_map[letter_pair[1]]\
                                      .union({letter_pair[1]})
                                      ):
                return(False)
        return(True)

    '''
    For the case where the words are different length, we will need one more subroutine. Since the words are of different lengths, we will assume the first input w is the shorter word.
    Then we will pad the input so that w ends with 2 blank characters '-' so that w-- and v_1v_2v_3 self.ray[1] v_4 (or v_1v_2v_5 self.ray[0] v_6) are the same length
    Therefore, we give a subroutine to process input pairs ('-', letter).
    '''

    #This is not used below. I'm keeping it around just in case I need it.
    def horocyclic_edge_checker_different_length(self) -> Automaton:
        '''
        This machine will check whether there is an uncancelable pair between two horocyclic suffixes of length differing by 1. The first input is w and the second is v.
        v_3 or v_5, depending on the form of v, is necessarily empty to have such an edge. However, this machine will not check this fact explicitly.
        The inputs will be pairs (w_letter, v_letter) or the pair ('-', '-'). The latter denotes the end of the word.
        
        The subroutines generate_states_without_uncancelables, generate_first_noncanceling_transitions, get_nonterminal_transitions,
        and get_single_blank_transition will all be defined later.
        
        :return: an Automaton which accepts pairs (w_1w_2w_3self.ray[1]w_4-, v_1v_2 v_6-) and (w_1w_2w_4 self.ray[0]w_6-, v_1v_2 v_4-) such that the lengths of each word are equal and there is no uncancelable pair
        '''

        #if not (mode == '1234' or mode == '1256'):
            #raise ValueError(''' The mode should be either '1234' or '1256' ''')

        #This dictionary keeps track of the necessary changes to the parameters n_v and n_w
        subword_dict = {}
        #The letters that commute with and precede both ray letters appear first in w_1
        for letter in self.c_map[self.ray[0]].intersection(self.lesser_star[self.ray[1]]):
            subword_dict[letter] = 1
        #The letters that commute with both ray letters and precede only the first appear first in w_2
        for letter in self.lesser_star[self.ray[0]].intersection(self.greater_star[self.ray[1]]):
            subword_dict[letter] = 2
        #Every other letter appears in one of the last two subwords, and these are all lumped into a single case.
        for letter in self.alphabet:
            try:
                subword_dict[letter]
            except KeyError:
                subword_dict[letter] = 3

        non_final_states = []
        Prefinal_states = []
        final_states = []
        total_transitions = []
        finished_states = []

        #The beginning of this machine is the same as the previous one. All that needs to change is that we need to check that there are precisely two input pairs ('-', 'letter').
        #Because of these two blank characters at the end of the word w, there is no need for an input ('-', '-') to indicate that the word has ended.
        
        (states_without_uncancelables, new_transitions) = self.generate_states_without_uncancelables(subword_dict)

        print('Completed the uncancelable states. There are ', len(states_without_uncancelables), ' of them.')
        
        non_final_states.extend(states_without_uncancelables)
        total_transitions.extend(new_transitions)
        
        for state_without_uncancelables in states_without_uncancelables:
            (new_states, new_transitions) = self.generate_first_noncanceling_transitions(state_without_uncancelables,subword_dict)
            non_final_states.extend(new_states)
            total_transitions.extend(new_transitions)
            finished_states.append(state_without_uncancelables)

        print('Completed the first batch of transitions. There are ', len(total_transitions), 'transitions and ', len(non_final_states), ' states in total')
        
        while len(non_final_states) > 0:
            source_state = non_final_states.pop(0)
            if source_state in finished_states:
                continue

            (new_states, new_transitions) = self.get_nonterminal_transitions(source_state, subword_dict)
            non_final_states.extend(new_states)
            total_transitions.extend(new_transitions)
            finished_states.append(source_state)

        print('Completed the nonterminal transitions. There are ', len(total_transitions), ' transitions and ', len(set(finished_states)), ' states in total')
        
        for source_state in set(finished_states):
            for letter in source_state.label()[9]:
                holder = self.get_single_blank_transition(source_state, letter, subword_dict)
                if holder is None:
                    continue
                (Prefinal_state, Prefinal_transition) = holder
                Prefinal_states.append(Prefinal_state)
                total_transitions.append(Prefinal_transition)

        print('Completed the first set of blank transitions. There are ', len(total_transitions), 'transitions and ', len(set(Prefinal_states)), ' pre-final states in total')

        for source_state in set(Prefinal_states):
            for letter in source_state.label()[9]:
                holder = self.get_single_blank_transition(source_state, letter, subword_dict)
                if holder is None:
                    continue
                (final_state, final_transition) = holder
                final_states.append(final_state)
                total_transitions.append(final_transition)

        print('Completed the second set of blank transitions. There are ', len(total_transitions), 'transitions and ', len(set(final_states)), ' final states in total')
        
        return Automaton(total_transitions)
        

    def get_single_blank_transition(self, source_state: FSMState, InputLetter: str, subword_dict: dict[str:int]) -> tuple:
        '''
        This method takes a source_state and returns the result of a transition labeled ('-', 'InputLetter').
    
        :param source_state: an instance of FSMState of the above form.
        :param InputLetter: The input letter of the subword v. This may be canceling or adding.
        :param subword_dict: A dictionary whose keys are letters and whose values are the first subword that letter appears in.
    
        :return: a pair (new_state, new_transition) if the input ('-', InputLetter) does not create an uncancelable pair. 
        new_transition is an instance of FSMTransition whose from_state is source_state and whose to_state is new_state.
        If an uncancelable pair is created, this method returns None.
        '''
        
        new_label = self._mutable_label(source_state.label())
        new_uncancelable_list = []
    
    
        #Subwords w_1 and w_2 have ended.
        new_n_v = max(new_label[10][1], subword_dict[InputLetter])
        new_label[10] = (3, new_n_v)
        
        #We will process this input in two cases depending on whether InputLetter is adding or cancelling. The adding case is easiest.
    
        if new_label[11]:
            new_label[2*new_n_v-2].append(InputLetter)
            for first_letters_set in new_label[2*new_n_v-1]:
                if InputLetter in first_letters_set[1]:
                    first_letters_set[0].add(InputLetter)
                first_letters_set[1].intersection_update(self.c_map[InputLetter])
            new_label[2*new_n_v-1].append( ({InputLetter},self.c_map[InputLetter]) )
            
        #We get a  bit flip in this case if NV < 3. 
            if new_n_v < 3:
                new_label[11] = False
                present_letter_list = new_label[0].word_as_list + new_label[2].word_as_list + new_label[4].word_as_list
                present_letters = set(present_letter_list)
                #Every previously cancelable letter will become uncancelable. 
                #This will create an uncancelable pair if any of them fail to cancel with one another or with the canceling_letter.
                #We also check whether there are any duplicates among the present_letters.
                if len(present_letter_list)>len(present_letters) or ( not self._test_set_commutation(present_letters)):
                    return(None)
                
                #Add every remaining cancelable letter into the uncancelable set
                new_label[8]=new_label[8].union(present_letters)
                for letter in present_letters:
                    new_label[9].intersection_update(self.c_map[letter])
            
                #Delete every previously cancelable letter, which appear only in v_1 and v_2
                for i in range(0,3):
                    new_label[2*i] = self.word_generator_machine.word([])
                    new_label[2*i+1] = []
                #The 12th entry of new_state.label() will count the number of ending transitions that have elapsed.
                try:
                    new_label[12] += 1
                except IndexError:
                    new_label.append(1)
                new_state = FSMState(self._hashable_label(new_label), is_final = (new_label[12] == 2))
                new_transition = FSMTransition(source_state, new_state, ('-', InputLetter))
                
                
                return(new_state, new_transition)
    
            #if the bit has not flipped, there is nothing left to do.
            try:
                new_label[12] += 1
            except IndexError:
                new_label.append(1)
            new_state = FSMState(self._hashable_label(new_label), is_final = (new_label[12] == 2))
            new_transition = FSMTransition(source_state, new_state, ('-', InputLetter))
            return (new_state, new_transition)

        #If the InputLetter is canceling, then the increase of NV may have created new uncancelable letters.
        new_uncancelable_list = []
        for i in range (0, new_n_v-1):
            new_uncancelable_list.extend(new_label[2*i].word_as_list)
            new_label[2*i] = self.word_generator_machine.word([])
            new_label[2*i+1] = []

        new_uncancelableset = set(new_uncancelable_list)
        Remainingletter_list = new_label[0].word_as_list + new_label[2].word_as_list + new_label[4].word_as_list
        remaining_letter_set = set(Remainingletter_list)

        #Check if this creates an uncancelable pair.

        if (len(new_uncancelable_list) > len(new_uncancelableset)) or ( not self._test_set_commutation(new_uncancelableset)) or ( not self._test_set_pair_commutation (new_uncancelableset, remaining_letter_set, True) ):
            return(None)

        #If there is no uncancelable pair, it is also possible to create a bit flip. It is not possible for n_v to be greater than 3, and the InputLetter is a letter of v.
        #Therefore, we only check if the InputLetter commutes with and follows every RemainingLetter.
        
        LettersFollowingAllremaining_letters = copy.copy(self.alphabet)
        for letter in remaining_letter_set:
            LettersFollowingAllremaining_letters.intersection_update(self.greater_star[letter])
        
        if InputLetter in LettersFollowingAllremaining_letters:
            #Every RemainingLetter will become uncancelable. Check whether this creates an uncancelable pair.
            if (len(Remainingletter_list) > len(remaining_letter_set) or not self._test_set_commutation(remaining_letter_set)):
                return(None)
            
            new_label[8] = new_label[8].union(remaining_letter_set)
            for letter in remaining_letter_set:
                    new_label[9].intersection_update(self.c_map[letter])
            for i in range(0,4):
                new_label[2*i] = self.word_generator_machine.word([])
                new_label[2*i+1] = []
                
            #the InputLetter becomes the only cancelable letter if it is in subword 3. Otherwise it becomes uncancelable as well.
            
            if new_n_v == 3:
                new_label[4] = self.word_generator_machine.word([InputLetter])
                new_label[5].append(({InputLetter}, self.c_map[InputLetter]))
                new_label[11] = True

                try:
                    new_label[12] += 1
                except IndexError:
                    new_label.append(1)
                new_state = FSMState(self._hashable_label(new_label), is_final = (new_label[12] == 2))
                new_transition = FSMTransition(source_state, new_state, ('-',InputLetter))
                return (new_state, new_transition)

            #The InputLetter becomes uncancellable. We know already that it commutes with every other letter.
            new_label[8].add(InputLetter)
            new_label[9].intersection_update(self.c_map[InputLetter])
            try:
                new_label[12] += 1
            except IndexError:
                new_label.append(1)
            new_state = FSMState(self._hashable_label(new_label), is_final = (new_label[12] == 2))
            new_transition = FSMTransition(source_state, new_state, ('-',InputLetter))
            return (new_state, new_transition)

        #If the bit has not flipped, then we process the InputLetter as a canceling letter.
        new_label = self.process_canceling_letter(new_label, InputLetter, subword_dict)
        if new_label is None:
            return (None)
        try:
            new_label[12] += 1
        except IndexError:
            new_label.append(1)
        new_state = FSMState(self._hashable_label(new_label), is_final = (new_label[12] == 2))
        new_transition = FSMTransition(source_state, new_state, ('-',InputLetter))
        return (new_state, new_transition)

    
       
        

    
