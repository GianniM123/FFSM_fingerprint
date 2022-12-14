import networkx as nx

RESET_IN = "RESET-SYS"
RESET_OUT = "epsilon"

def unify_configs(current_variants : set[str], new_variants : set[str]) -> set[str]:
    if current_variants == set():
        return new_variants
    elif new_variants == set():
        return current_variants
    
    equal_variants = current_variants.intersection(new_variants)
    return equal_variants

class ConditionalState():
    
    def __init__(self, state_id : str, features : set[str]):
        self.state_id = state_id
        self.features = features
        self.transitions : dict[str,dict[str,ConditionalState]] = {}
        self.outputs : dict[str,dict[str,str]] = {}

    def __eq__(self, other) -> bool:
        if isinstance(other,ConditionalState):
            return self.state_id == other.state_id
        return False
    def __hash__(self):
        return hash(self.state_id)    
    def __str__(self) -> str:
        return "(" + self.state_id + ", " + self.features.__str__() + ")"


class FFSM():
    
    def __init__(self, states: list[ConditionalState], initial_state: ConditionalState, features : set[str]):
        self.initial_state = initial_state
        
        self.state_map : dict[str,ConditionalState] = {}
        for state in states:
            self.state_map[state.state_id] = state

        self.alphabet = set()
        self.states : list[ConditionalState] = states
        for state in self.states:
            for input in state.transitions.keys():
                self.alphabet.add(input)
        self.alphabet = set(sorted(self.alphabet))
        self.features = features
        self.reset_to_initial_state()      

    @classmethod
    def from_file(self, file: str) -> 'FFSM':
        ffsm : nx.MultiDiGraph = nx.drawing.nx_agraph.read_dot(file)

        all_features = set(ffsm.graph["configurations"].split("|"))

        states : dict[str,ConditionalState] = {}
        all_states = []
        for state in ffsm.nodes.data():
            features = state[1]["feature"].split("|")
            if features[0] == "True":
                features = all_features
            if state[0] != "__start0":
                new_state = ConditionalState(state[0],set(features))
                states[state[0]] = new_state
                all_states.append(new_state)
 
        initial_state = None
        for transition in ffsm.edges.data():
            if transition[0] == "__start0":
                initial_state = states[transition[1]]
                continue
            in_output = transition[2]["label"].split("/")
            features = transition[2]["feature"].split("|")
            input = in_output[0].replace(" ", "")
            output = in_output[1].replace(" ", "")

            for feature in features:
                if input not in states[transition[0]].transitions.keys():
                    states[transition[0]].outputs[input] = {feature: output}
                    states[transition[0]].transitions[input] = {feature: states[transition[1]]}
                else:
                    states[transition[0]].outputs[input][feature] = output
                    states[transition[0]].transitions[input][feature] = states[transition[1]]
        
        
        
        return FFSM(all_states, initial_state, all_features)
        
    def __str__(self) -> str:
        output = ""
        for transition in self.transitions:
            output = output + transition.__str__()
        return output

    def __eq__(self, other) -> bool:
        if isinstance(other, FFSM):
            return self.current_states == other.current_states and self.alphabet == other.alphabet and self.features == other.features and self.initial_state == other.initial_state and self.states == other.states


    def step(self, input : str, features_in : set[str] = set()) -> list[tuple[str, set[str]]]:
        new_current_states : dict[ConditionalState, set[str]] = {}
        outputs : dict[str, set[str]] = {}
        for current_state, feature_config in self.current_states:
            features = unify_configs(feature_config, features_in)
            for feature in features:
                new_state = current_state.transitions[input][feature]
                output = current_state.outputs[input][feature]
                if output in outputs.keys():
                    outputs[output].add(feature)
                else:
                    outputs[output] = {feature}
                if new_state in new_current_states.keys():
                    new_current_states[new_state].add(feature)
                else:
                    new_current_states[new_state] = {feature}
                                 
                        
        if len(new_current_states) == 0:
            raise Exception("Invalid input: ", input, " given the state: ", self.current_states)
        else:
            for key in new_current_states.keys():
                new_current_states[key] = frozenset(new_current_states[key])
            self.current_states = set(new_current_states.items())
        return list(outputs.items())

    def make_input_complete(self) -> None:
        for state in self.states:
            input_dict = {}
            for input in self.alphabet:
                input_dict[input] = set()
                if input in state.transitions.keys():
                    for features in state.transitions[input].keys():
                        input_dict[input] = input_dict[input].union({features})

            for input, features in input_dict.items():
                feature_diff = state.features.difference(features)
                for feature in feature_diff:
                    if input not in state.transitions.keys():
                        state.transitions[input] = {feature : state}
                        state.outputs[input] = {feature : 'epsilon'}
                    else:
                        state.transitions[input][feature] = state
                        state.outputs[input][feature] = 'epsilon'
                        

    def add_resets(self):
        self.alphabet.add(RESET_IN)
        for feature in self.features:
            for state in self.states:
                if RESET_IN not in state.transitions.keys():
                    state.transitions[RESET_IN] = {feature : self.initial_state}
                    state.outputs[RESET_IN] = {feature: RESET_OUT}
                else:
                    state.transitions[RESET_IN][feature] = self.initial_state
                    state.outputs[RESET_IN][feature] = RESET_OUT


    def reset_to_initial_state(self, features : set[str] = None) -> None:
        if features == None:
            self.current_states : set[tuple[ConditionalState, frozenset[str]]] = {(self.initial_state, frozenset(self.features))}
        else:
            self.current_states : set[tuple[ConditionalState, frozenset[str]]] = {(self.initial_state, frozenset(features))}

    def get_transitions(self):
        transitions : list[tuple[tuple[str,set[str]],tuple[str,set[str]],tuple[str,set[str]],str]] = []

        for state in self.states:
            for input, feature_dict in state.transitions.items():
                for feature, to_state in feature_dict.items():
                    transitions.append(((state.state_id,state.features),(to_state.state_id,to_state.features),(input,feature),state.outputs[input][feature]))
        
        return transitions
