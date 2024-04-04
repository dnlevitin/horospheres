from sage.combinat.finite_state_machine import Automaton, FSMState, FSMTransition

def generate_geodesic_machine(alphabet:set, commutation_dict:dict[str:set], order_dict:dict[str:int], mode:str) -> Automaton:
        """
        Generate an Automaton that prevents letters from being written that cancel. 
        The states of this automaton represent the list of letters that a word cannot be followed by if it is to remain geodesic.
        Each state's label tells us which letters can follow it. We therefore construct the Automaton by a BFS.

        :param alphabet: a set of all the letters present. These represent order-2 generators of the group
        :param commutation_dict: a dictionary describing which pairs of letters commute. commutation_dict[key] is the set of letters that the key commutes with.
        :param order_dict: any ordering of the letters in the alphabet. Used to transform sets into tuples unambiguously.
        :param mode: either 'objects' or 'labels'. In 'objects' mode, we will generate FSMTransition instances between FSMState instances. In 'labels' mode we will just record the defining data.

        :return: An Automaton whose accepted language consists of geodesic words.
        """
        
        
        if mode == 'objects':
            start_state = FSMState(tuple(), is_initial = True, is_final = True)
        if mode == 'labels':
             start_state = tuple()

        transition_list = []
        frontier = []
        finished_states = []
        
 
        for nextletter in alphabet:
            next_name = tuple(nextletter)

            if mode == 'objects':
                next_state = FSMState(next_name, is_initial = False, is_final = True)
                transition_list.append(FSMTransition(start_state, next_state, nextletter))
            if mode == 'labels':
                 next_state = next_name
                 transition_list.append((start_state, next_state, nextletter))
            
            frontier.append(next_state)

        finished_states.append(start_state)

        while frontier:
            source_state = frontier.pop(0)
            if source_state in finished_states:
                continue
            
            if mode == 'objects':
                source_set = set(source_state.label())
            if mode == 'labels':
                 source_set = set(source_state)

            #The legal next letters are exactly those not forbidden by the label of the current state)
            for nextletter in alphabet.difference(source_set):
                # This line computes the new set of forbidden letters
                next_set = source_set.intersection(commutation_dict[nextletter]).union({nextletter})
                next_name = tuple(sorted(next_set, key = lambda x: order_dict[x]))

                if mode == 'objects':
                    #This line creates a new FSMState instance, which may be fully equal to an instance that exists already.
                    #In fact, pairs of fully equal FSMStates are created often.
                    next_state = FSMState(next_name, is_initial = False, is_final = True)
                    transition_list.append(FSMTransition (source_state, next_state, nextletter))
                if mode == 'labels':
                    next_state = next_name 
                    transition_list.append((source_state, next_state, nextletter))
                                
                frontier.append(next_state)
                
               
            finished_states.append(source_state)

        if mode == 'objects':
            #In this mode we only need to pass the transition list.
            return (Automaton(transition_list))
        if mode == 'labels':
            #In this mode we must additionally specify which the labels of the initial and final states are.
            return (Automaton(transition_list, [start_state], finished_states))

commutation_dict = {'a': {'b', 'e'}, 'b': {'a', 'c'}, 'c': {'b', 'd'}, 'd': {'e', 'c'}, 'e': {'a', 'd'}}
order_dict = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4}
alphabet = {'a', 'b', 'c', 'd', 'e'}

#Choose a desired mode
mode = 'objects'
#mode = 'labels'

geodesic_machine = generate_geodesic_machine(alphabet, commutation_dict, order_dict, mode)

#These assertions tell us that the machine has the expected number of states and transitions.
assert(len(geodesic_machine.states()) == 11)
assert(len(geodesic_machine.transitions()) == 40)

#This assertion works fine. It says that the word 'a' is geodesic, which is true.
assert(geodesic_machine.process( ['a'] )[0])

#This assertion works fine. It says that there is an outgoing edge from the state ('a') labeled 'c'.
transition_list = geodesic_machine.transitions(geodesic_machine.state(geodesic_machine.process( ['a'] )[1]))
assert(any( transition.word_in [0] == 'c' for transition in transition_list ))

#In 'objects' mode, this assertion throws the error 'ValueError: State ('c',) does not belong to a finite state machine.'
#In 'labels' mode, this assertion works fine, telling us that the word 'ac' is gedesic, which is true.
assert(geodesic_machine.process( ['a', 'c'] )[0])