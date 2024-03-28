#This module provides minimum specifications for an automaton. It is an approximate recreation of the features in sage.combinat.finite_state_machine
#One issue I'm going to run into is the possibility that I declare different state instances with the same data
#This should be fine as long as every time I need them they get hashed (e.g. they get put into a set, tested ==, or put into a dictionary)
from sage.structure.sage_object import SageObject
import typing
from itertools import product

class FSMState(SageObject):
    
    def __init__(self, label, is_initial = False, is_final = False):
        if not hasattr(label, typing.Hashable):
            raise TypeError('State Labels must be hashable')
        if type (is_initial) != bool:
            raise TypeError('parameter is_initial should be a boolean')
        if type(is_final) != bool:
            raise TypeError('parameter is_final should be a boolean')
        self._label = label
        self._is_initial = is_initial
        self._is_final = is_final

    @property
    def label(self):
        return self._label
    
    @property
    def is_initial(self) -> bool:
        return self._is_initial
    
    @property
    def is_final(self) -> bool:
        return self._is_final
    
    def __hash__(self):
        #This will check more than label equality. As a result, we will need to check manually that our states have distinct names.
        return hash((self.label, self.is_initial, self.is_final))
    
    def __eq__(self, other):
        if not isinstance(other, FSMState):
            return False
        return self.label == other.label and (not self.is_initial ^ other.is_initial) and (not self.is_final ^ other.is_final)
        
    def __ne__(self, other):
        return not self == other
    
    def __repr__(self) -> str:
        return('FSMState with label ' + str(self.label) + '. it %(initial)s initial and %(final)s final.' %{'initial': ['is not', 'is'][int(self.is_initial)], 'final':['is not', 'is'][int(self.is_final)]})

class FSMTransition(SageObject):
    
    def __init__(self, from_state: FSMState, to_state: FSMState, word_in):
        if (not isinstance(from_state, FSMState)) or (not isinstance(to_state, FSMState)):
            raise TypeError('The FSMTransition constructor must be passed instances of FSMState')
        if from_state.label == to_state.label and from_state != to_state:
            raise ValueError('Transitions are disallowed between unequal states of the same label')
        if not hasattr(word_in, typing.Hashable):
            raise TypeError('Transition labels must be hashable')
        self._from_state = from_state
        self._to_state = to_state
        self._word_in = word_in
    
    @property
    def from_state(self) -> FSMState:
        return self._from_state
    @property
    def to_state(self) -> FSMState:
        return self._to_state
    @property
    def word_in(self):
        return self._word_in
    
    def __eq__(self, other):
        #Note that two transitions will evaluate as unequal if they have from_states or to_states with the same label but different is_initial or is_final values
        if not isinstance(other, FSMTransition):
            return False
        return self.from_state == other.from_state and self.to_state == other.to_state and self.word_in == other.word_in
    def __ne__(self,other):
        return not self == other
    
    def __hash__(self):
        return hash((self.to_state, self.from_state, self.word_in))
    
    def __repr__(self):
        return('FSMTransition from ' + str(self.from_state.label) + ' to ' + str(self.to_state.label) + ' labeled by ' + str(self.word_in))

    
class Automaton(SageObject):
    
    def __init__(self, state_set:set[FSMState], transition_set:set[FSMTransition]):
        if not isinstance(state_set, set):
            raise TypeError('the first parameter should be a set')
        if not all(isinstance(state, FSMState) for state in state_set):
            raise TypeError('parameter state_set should consist of instances of FSMState')
        if not isinstance(transition_set, set):
            raise TypeError('the second parameter should be a set')
        if not all(isinstance(transition, FSMTransition) for transition in transition_set):
            raise TypeError('parameter transition_set should consist of instances of FSMTransition')
        for i in range(0, len(state_set)):
            for j in range (i+1, len(state_set)):
                if state_set[i].label == state_set[j].label:
                    raise ValueError('No automata are allowed to have multiple states with the same label')
                
        for transition in transition_set:
            if not (transition.from_state in state_set and transition.to_state in state_set):
                raise ValueError('parameter state_set must contain every state used in the transitions')

        state_list = list(state_set)   
        initiality_list = [int(state.is_initial) for state in state_list]
        if sum(initiality_list) == 0:
            raise ValueError('No initial state provided')
        if sum(initiality_list) > 1:
            raise ValueError('Only one initial state is permitted')
        
        
        finality_list = [state.is_final for state in state_set]
        if not any(finality_list):
            raise ValueError('No final state provided')
        

        self._states = state_set
        self._transitions = transition_set
        self._initial_state = state_list[initiality_list.index(True)]
        self._final_states = {state for state in state_set if state.is_final}
        self._dict = {}
        for state in self._states:
            self._dict[state] = {}
        for transition in self._transitions:
            try:
                self._dict[transition.from_state][transition.word_in]
            except KeyError:
                self._dict[transition.from_state][transition.word_in] = transition.to_state
            else:
                raise ValueError('Automata must be deterministic')
        
    @property
    def states(self) -> set[FSMState]:
        return self._states
    
    @property
    def initial_state(self) -> FSMState:
        return self._initial_state
    
    @property
    def final_states(self) -> set[FSMState]:
        return self._final_states
    
    @property
    def dict(self) -> dict[FSMState: dict[ : FSMState]]:
        return self._dict

    def state(self, label) -> FSMState:
        
        if not hasattr(label, typing.Hashable):
            raise TypeError('All labels are hashable. The provided input is not')

        for state in self.states:
            if state.label == label:
                return state
            
        raise ValueError('No state of this label found')
    
    def transition(self, from_state:FSMState, to_state:FSMState, word_in) -> FSMTransition:
        #Technically this returns a new FSMTransition rather than the one in the Automaton. This may cause problems.
        if (not isinstance(from_state, FSMState)) or (not isinstance(to_state, FSMState)):
            raise TypeError('parameters from_state and to_state must be instances of FSMState')
        if not hasattr(word_in, typing.Hashable):
            raise TypeError('Transition labels must be hashable')
        
        #It may create problems for these errors to be of the same type.
        try:
            if self.dict[from_state][word_in] == to_state:
                return FSMTransition(from_state, to_state, word_in)
            raise ValueError('Transition found that matches from_state and word_in, but not to_state')
        except KeyError:
            raise ValueError('This from_state has no transition of the desired word_in')
        
    def transitions(self, from_state = None) -> set[FSMTransition]:
        #It may cause problems that, if passed a specific starting state, this returns new FSMTransitions matching the existing ones, rather than the existing ones themselves.

        if from_state == None:
            return self._transitions
        if not isinstance(from_state, FSMState):
            raise TypeError('Parameter from_state must be an instance of FSMState')
        if not from_state in self.states:
            raise ValueError('This state does not belong to this automaton')
        outgoing_transitions = set()
        for (word_in, to_state) in self.dict[from_state].items():
            outgoing_transitions.add(FSMTransition(from_state, to_state, word_in))
        return outgoing_transitions
    
    def intersection(self, other) -> Automaton:
        if not isinstance(other, Automaton):
            raise TypeError ('Can only take the fiber product of two automata')
        
        state_set = set()
        transition_set = set()
        has_final_state = False

        frontier = []
        finished_states = set()

        initial_state = FSMState( (self.initial_state.label , other.initial_state.label), True, self.initial_state.is_final and other.initial_state.is_final)
        state_set.add(initial_state)
        if initial_state.is_final:
            has_final_state = True

        for key in self.dict[self.initial_state].keys():
            try:
                other_new_state = other.dict[other.initial_state][key]
            except KeyError:
                continue
            else:
                self_new_state = self.dict[self.initial_state][key]
                new_state = FSMState( (self_new_state.label, other_new_state.label) , self_new_state.is_initial and other_new_state.is_initial, self_new_state.is_final and other_new_state.is_final )
                state_set.add(new_state)
                new_transition = FSMTransition(initial_state, new_state, key)
                frontier.append(new_state)
                transition_set.add(new_transition)
                if (not has_final_state) and new_state.is_final:
                    has_final_state = True

        finished_states.add(initial_state)
        

        while frontier:
            state = frontier.pop(0)
            if state in finished_states:
                continue
            for key in self.dict[state.label[0]].keys():
                try:
                    other_new_state = other.dict[state.label[1]][key]
                except KeyError:
                    continue
                else:
                    self_new_state = self.dict[self.initial_state][key]
                    new_state = FSMState( (self_new_state.label, other_new_state.label) , self_new_state.is_initial and other_new_state.is_initial, self_new_state.is_final and other_new_state.is_final )
                    state_set.add(new_state)
                    new_transition = FSMTransition(state, new_state, key)
                    frontier.append(new_state)
                    transition_set.add(new_transition)
                    if (not has_final_state) and new_state.is_final:
                        has_final_state = True
            finished_states.add(state)

        if not has_final_state:
            raise ValueError('No final state is reached. That is, the corresponding languages have empty intersection')
        
        return(Automaton(state_set, transition_set))

    def concatenation(self, other):

        #This operation does not have all the desired features of concatenation in a general deterministic automaton. However, it is sufficient for my purposes.
        #In particular, it raises an error in the event of a necessary (but not sufficient) condition the concatenation not to be deterministic.
        #In general, the concatenation can be determinized. However, this module does not implement the determinization algorithm.

        if not isinstance(other, Automaton):
            raise TypeError ('Can only take the fiber product of two automata.')
        
        if self.states.intersection(other.states) != set():
            raise ValueError ('Cannot concatenate automata when they share states.')
        #This also implies that the sets of transitions are disjoint
        
        letters_after_self_final_states = set()
        for final_state in self.final_states:
            letters_after_self_final_states.update(set(self.dict[final_state].keys()))
        
        if letters_after_self_final_states.intersection(set(other.dict[other.initial_state].keys())) != set():
            raise ValueError ('It is unclear if this will be deterministic.')
        
        #If the second automaton does not accept the empty word, then we cannot allow any state in the first automaton to be final.
        #This set will keep track of the states that were final in self, whether or not they are supposed to be final in the resulting automaton.
        first_final_state_set = set()
        if other.initial_state.is_final:
            state_set = (self.states.union(other.states)).difference({other.initial_state})
            first_final_state_set = self.final_states
        else:
            nonfinalized_first_states = set()
            for state in self.states:
                if state.is_final:
                    nonfinalized_first_states.add(FSMState(state.label, state.is_initial, False))
                    first_final_state_set.add(FSMState(state.label, state.is_initial, False))
                else:
                    nonfinalized_first_states.add(state)

        transition_set = (self.transitions.union(other.transitions)).difference(other.transitions(other.initial_state))

        for first_final_state in first_final_state_set:
            for transition in other.transitions(other.initial_state):
                #Edge case: loops in other from the starting state.
                if transition.to_state == other.initial_state:
                    new_transition = FSMTransition(first_final_state, first_final_state, transition.word_in)
                    transition_set.add(new_transition)
                    continue

                new_transition = FSMTransition(first_final_state, transition.to_state, transition.word_in)
                transition_set.add(new_transition)
        
        return(Automaton(state_set, transition_set))

    def process(self, input_tape):
        
        if not hasattr(input_tape, typing.Iterable):
            raise TypeError('The input tape should be an iterable')
        
        current_state = self.initial_state

        for input in input_tape:
            try:
                current_state = self.dict[current_state][input]
            except KeyError:
                return (False, None)
        
        return (current_state.is_final, current_state.label)