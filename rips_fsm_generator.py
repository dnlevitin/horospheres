from sage.combinat.finite_state_machine import FSMState, FSMTransition
from enhanced_automaton import EnhancedAutomaton

class RipsFSMGenerator:
    def __init__(self, commutation_dict:dict[str, set], 
                 order_dict: dict[str, int], ray: tuple[str]):
        
        '''
        This object will make the necessary automata for the 2- Rips
         graph on a horosphere.
    
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
            raise ValueError ("The defining ray consists of two letters which commute")
        
        if len(order_dict.values()) != len(set(order_dict.values())):
            raise ValueError ('The provided order is not a total order')

        self.c_map = commutation_dict
        self.o_map = order_dict
        self.alphabet = set().union(letter for letter in self.o_map)
        self.ray = ray

        for letter in self.alphabet:
            for adjacent_letter in self.alphabet[letter]:
                if not letter in self.c_map[adjacent_letter]:
                    raise ValueError('Parameter commutation_dict is not symmetric')

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

    
    def first_letter_excluder(self, excluded_letters:set) -> \
        EnhancedAutomaton:

        '''
        Generate an automaton that prevents a chosen set of letters from
         reaching the beginning of the word without cancellation. 
         The states in this machine represent which letters could still
         reach the beginning of the word.
        
        :param excluded_letters: A set of letters which that accepted
         words should not begin with.
                
        :return: An automaton that accepts words which, without 
         cancellation, cannot be commuted to begin with a letter in 
         excluded_letters
        '''
        
        if excluded_letters == self.alphabet:
            single_state = FSMState('origin', is_initial = True, is_final = True)
            return EnhancedAutomaton({single_state:[]})
        sorted_excluded_letters = sorted(excluded_letters,
                                         key = lambda x: self.o_map[x])
        transition_list = []
        frontier = []
        state_list = []
        start_state_name = tuple(sorted_excluded_letters)
        state_list.append(start_state_name)
        
        for next_letter in self.alphabet.difference(excluded_letters):
            next_name = tuple(sorted(excluded_letters.intersection(
                self.c_map[next_letter]), key = lambda x: self.o_map[x]))
            transition_list.append((start_state_name, next_name, next_letter))
            if not next_name in state_list:
                state_list.append(next_name)
            frontier.append(next_name)
            
        #Find further states by a BFS
        
        finished_states = [start_state_name]
        while frontier:
            source_sate = frontier.pop(0)
            if source_sate in finished_states:
                continue
        
            source_set = set(source_sate)
            for next_letter in self.alphabet.difference(source_set):
                next_name = tuple(sorted(source_set.intersection(
                    self.c_map[next_letter]), key = lambda x: self.o_map[x]))
                frontier.append(next_name)
                transition_list.append((source_sate, next_name, next_letter))
            if not next_name in state_list:
                state_list.append(next_name)

            finished_states.append(source_sate)
            
        return(EnhancedAutomaton(transition_list, [start_state_name], state_list))
        
    def shortlex_machine(self, restricted_alphabet=None) -> EnhancedAutomaton:

        """
        Generate an FSM that prevents letters from being written that either
         cancel or should have already been written. 
        The states of this automaton represent the list of letters that
        a word cannot be followed by if it is to remain shortlex.

        :param restricted_alphabet: if desired, pass a subset of 
         self.alphabet to get the shortlex machine for the special 
         subgroup defined by the vertices in restricted_alphabet. 
         If this set is empty, an automaton recognizing the empty word
         is returned.
        
        :return: An automaton whose accepted language consists of 
         shortlex words spelled with letters of `restricted_alphabet`.
        """

        if restricted_alphabet is None:
            restricted_alphabet = self.alphabet
        if not restricted_alphabet.issubset(self.alphabet):
            raise ValueError('argument restricted_alphabet is not a subset of \
                             self.alphabet')
        if restricted_alphabet == set():
            single_state = FSMState('origin', is_initial = True, is_final = True)
            return EnhancedAutomaton({single_state:[]})
        
        start_state = ()
        transition_list = []
        frontier = []
        states = [start_state]
        finished_states = []

        # Compute the legal next letters for single letter words.
        for next_letter in restricted_alphabet:

            # Compute the set of legal next letters for each letter.
            next_name = tuple(sorted((self.lesser_star[next_letter]\
                                      .intersection(restricted_alphabet))\
                                      .union({next_letter}),
                                        key = lambda x: self.o_map[x]))
            transition_list.append((start_state, next_name, next_letter))
            if not next_name in states:
                states.append(next_name)
            frontier.append(next_name)

        finished_states.append(start_state)

        # Run a BFS until we have finished the machine.
        while frontier:
            source_sate = frontier.pop(0)
            if source_sate in finished_states:
                continue

            source_set = set(source_sate)
            for next_letter in restricted_alphabet.difference(source_set):
                # This line computes the new set of forbidden letters.
                next_set = source_set.intersection(self.c_map[next_letter])\
                    .union(self.lesser_star[next_letter]\
                           .intersection(restricted_alphabet))\
                    .union({next_letter})
                next_name = tuple(sorted(next_set, key = lambda x: self.o_map[x]))
                

                if not next_name in states:
                    states.append(next_name)
                                
                frontier.append(next_name)
                transition_list.append((source_sate, next_name, next_letter))
            
            finished_states.append(source_sate)
               
        #This language is prefix-closed, so every state is final.
        
        #print(f"ShortLex Machine on alphabet {restricted_alphabet} Completed: Graph with \n\t\t{len(states)} Vertices and \n\t\t{len(transition_list)} Edges.")
        return (EnhancedAutomaton(transition_list, [start_state], states))
    
    def geodesic_machine(self, restricted_alphabet=None) -> EnhancedAutomaton:
        """
        Generate an FSM that prevents letters from being written that
         cancel. 
        The states of this automaton represent the tuple of letters that
         a word cannot be followed by if it is to remain geodesic.

        :param restricted_alphabet: if desired, pass a subset of 
         self.alphabet to get the geodesic machine for the special 
         subgroup defined by the vertices in restricted_alphabet.
        
        :return: An automaton whose accepted language consists of
         geodesic words spelled with letters of `restricted_alphabet`.
        """
        if restricted_alphabet is None:
            restricted_alphabet = self.alphabet
        if not restricted_alphabet.issubset(self.alphabet):
            raise ValueError("argument restricted_alphabet is not a subset of\
                             self.alphabet")
        if restricted_alphabet == set():
            single_state = FSMState('origin', is_initial = True, is_final = True)
            return EnhancedAutomaton({single_state:[]})
        
        start_state = ()
        transition_list = []
        frontier = []
        finished_states = []
        states = [start_state]

        # Compute the legal next letters for single letter words. 
        for next_letter in restricted_alphabet:

            # Compute the set of legal next letters for each letter.
            next_name = tuple(next_letter)
            transition_list.append((start_state, next_name, next_letter))
            states.append(next_name)
            
            frontier.append(next_name)
        
        finished_states.append(start_state)

        # Run a BFS until we have finished the machine.
        while frontier:
            source_sate = frontier.pop(0)
            if source_sate in finished_states:
                continue

            source_set = set(source_sate)
            for next_letter in restricted_alphabet.difference(source_set):
                # This line computes the new set of forbidden letters
                next_set = source_set.intersection(self.c_map[next_letter])\
                    .union({next_letter})
                next_name = tuple(sorted(next_set, key = lambda x: self.o_map[x]))
                                
                # Add NextState to our frontier to ensure all vertices are reached
                frontier.append(next_name)
                if not next_name in states:
                    states.append(next_name)
                transition_list.append((source_sate, next_name, next_letter))

            finished_states.append(source_sate)

        #This language is prefix-closed, so every state is final.

        #print(f"Geodesic Machine on alphabet {restricted_alphabet} completed: Graph with \n\t\t{len(states)} Vertices and \n\t\t{len(transition_list)} Edges.")
        return (EnhancedAutomaton(transition_list, [start_state], states))
    
    def shortlex_suffix_machine(self) -> EnhancedAutomaton:
        return self.__shortlex_machine().enhanced_intersection(
            self.first_letter_excluder(set(self.ray)))

    def geodesic_suffix_machine(self) -> EnhancedAutomaton:
        return self.__geodesic_machine().enhanced_intersection(
            self.first_letter_excluder(set(self.ray)))