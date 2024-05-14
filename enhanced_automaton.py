from __future__ import annotations
from sage.combinat.finite_state_machine import Automaton, FSMState, FSMTransition

class EnhancedAutomaton(Automaton):


    '''
    This is the class of automata that will be used for this paper.
    In particular, the automata in this paper support a faster
    implementation of `Automaton.concatenation`.
    '''

    def __init__(self, *args, **kwargs):
        """
        This is the initialization statement copied for automata
        """
        super().__init__(*args, **kwargs)
    
    def unambiguous_concatenation(self, other: EnhancedAutomaton)-> \
        EnhancedAutomaton:
        '''
        A custom concatenation function for instances of 
        `EnhancedAutomaton` with languages L_1 and L_2,
        satisfying the following:

        (1) M_1 and M_2 have no epsilon transitions
        (2) No word of L_1 ends with a letter that a word of L_2 begins
         with.
        (3) L_2 contains the empty word.

        The code is a modification of the `.concatenation(other)` method
         from `sage.combinat.finite_state_machine`.
        If (2) is not satisfied, this should output a non-deterministic
         automaton recognizing L_1L_2
    
        :param other: a non-empty `EnhancedAutomaton`.

        :return: an `EnhancedAutomaton` without epsilon transitions
         recognizing the concatenated language L_1L_2
        '''

        # Edge case: two singleton automata recognizing the empty word.
        if len(self.states()) == 1 and  len(self.transitions()) == 0:
            if len(other.states()) == 1 and len(other.transitions()) == 0:
                # The state is relabeled as it would be in the code that
                # follows.
                single_state = FSMState((0, 'origin'), is_initial = True,
                                        is_final = True)
                return EnhancedAutomaton({single_state:[]})


        transition_list = []
        first_states = {}
        second_states = {}
        for s in self.iter_states():
            new_state = s.relabeled((0, s.label()))
            first_states[s] = new_state
            # Unlike in `Automaton.concatenation`, we allow
            # these states to be final when the state they are copying is
            # final. This means that each word w_1 in L_1 will again be 
            # accepted by the result, without needing an epsilon 
            # transition to a starting state of M_2.

        for s in other.iter_states():
            new_state = s.relabeled((1, s.label()))
            new_state.is_initial = False
            second_states[s] = new_state

        for t in self.iter_transitions():
            new_transition = FSMTransition(first_states[t.from_state],
                                          first_states[t.to_state],
                                          t.word_in,
                                          t.word_out)
            transition_list.append(new_transition)

        for t in other.iter_transitions():
            if (t.from_state).is_initial:
                continue
            new_transition = FSMTransition(second_states[t.from_state],
                                          second_states[t.to_state],
                                          t.word_in,
                                          t.word_out)
            transition_list.append(new_transition)

        for s in self.iter_final_states():
            first_state = first_states[s]
            for t in other.iter_initial_states():
                # Unlike in `Automaton.concatenation`, we create
                # labeled transitions directly to those states in `other`
                # that immediately follow initial states. 
                # This avoids the creation of epsilon transitions.
                for transition in other.transitions(t):
                    new_transition = FSMTransition (first_state,
                                                   second_states[transition.to_state],
                                                   transition.word_in,
                                                   transition.word_out)
                    transition_list.append(new_transition)
   
        return EnhancedAutomaton(transition_list)

    def enhanced_intersection(self, other: 'EnhancedAutomaton',
                              only_accessible_components=True)->\
                                  'EnhancedAutomaton':
        #Compute `self.intersection(other)` as in `Automaton`,
        #but return an `EnhancedAutomaton`.

        return EnhancedAutomaton(
            self.intersection(other, only_accessible_components))
    
    def _interspersal(self, other: EnhancedAutomaton) -> EnhancedAutomaton:
        '''
        Let the languages L_0 and L_1 be recognized respectively by 
        `self` and `other`. This method takes the union of the 
        even-length words in L_0 and the odd-length words in L_1.

        This function will not be used in practice in the main methods.
        However, some of the resulting automata are described in the
        paper, so this function is included for completeness.
        
        :param self: An `EnhancedAutomaton`.
        :param other: An `EnhancedAutomaton`.

        :return: An `EnhancedAutomaton` recognizing the even-length 
         words accepted by `self` and the odd length words accepted by
         `other`.     
        '''
        
        self.input_alphabet = set(self.input_alphabet).union(set(other.input_alphabet))
        other.input_alphabet = set(self.input_alphabet).union(set(other.input_alphabet))
        
        complete_self = self.completion()
        complete_other = other.completion()
        
        #Define an automaton to keep track of the length parity.
        
        even_state = FSMState(0, is_initial = True, is_final = True)
        odd_state = FSMState(1, is_initial = False, is_final = True)
        transition_list = []
        for letter in set(self.input_alphabet).union(set(other.input_alphabet)):
            transition_list.append(FSMTransition(even_state, odd_state, letter))
            transition_list.append(FSMTransition(odd_state, even_state, letter))
        parity_machine = EnhancedAutomaton(transition_list)
        
        #Because all these machines are complete, 
        #`complete_self.enhanced_intersection(complete_other)` 
        #will still track progress in `other` of a word rejected by
        #`self`, and vice versa.
        approx_machine = parity_machine.enhanced_intersection(
            complete_self.enhanced_intersection(complete_other))
        
        
        # As things are now, the states `(n, foo, bar))` are final,
        # where `foo` and `bar` are states of `self` and `other`
        # respectively, iff both `n, foo` and `n, bar` are final.
        # This cannot happen, so this automaton has the
        # correct states but no final states.
    
        # Labels are of the form 
        # `(n, (self.state(foo), other.state(bar)))`
        # We need n.label() to get the parity.

        for state in approx_machine.iter_states():    
            parity = (state.label()[0]).label()
            state.is_final = state.label()[1].label()[parity].is_final

        return approx_machine


    def next_letters(self, state: FSMState) -> set:
        '''
        Generate the collection of letters that label the transitions
         exiting a particular state.
        Note that transitions that do not lead to final states are 
         included, as are transitions to fail states (i.e. those from 
        which it is impossible to reach a final state)

        :param state: an `FSMState` of `self`.
        :return: the set of letters that can be written after `state`.
        '''

        if not self.has_state(state):
            raise ValueError('The state', state.label(), 
                             'is not in this machine.')

        # Recall that transition.word_in returns a singleton list.
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
