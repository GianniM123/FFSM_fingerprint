import networkx as nx

RESET_IN = "RESET-SYS"
RESET_OUT = "epsilon"

def unify_features(current_variants : set[str], new_variants : set[str]) -> set[str]:
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
        self.transitions : dict[str,dict[frozenset[str],ConditionalState]] = {}
        self.outputs : dict[str,dict[frozenset[str],str]] = {}

    def __eq__(self, other) -> bool:
        if isinstance(other,ConditionalState):
            return self.state_id == other.state_id
        return False
    
    def __str__(self) -> str:
        return "(" + self.state_id + ", " + self.features.__str__() + ")"


class FFSM():
    
    def __init__(self, states: list[ConditionalState], initial_state: ConditionalState, features : set[str]):
        self.initial_state = initial_state
        
        self.alphabet = set()
        self.states : list[ConditionalState] = states
        for state in self.states:
            for input in state.transitions.keys():
                self.alphabet.add(input)
        self.features = features
        self.reset_to_initial_state()      

    @classmethod
    def from_file(self, file: str) -> 'FFSM':
        ffsm = nx.drawing.nx_agraph.read_dot(file)

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
            features = set(transition[2]["feature"].split("|"))
            input = in_output[0].replace(" ", "")
            output = in_output[1].replace(" ", "")

            if input not in states[transition[0]].transitions.keys():
                states[transition[0]].outputs[input] = {frozenset(features) : output}
                states[transition[0]].transitions[input] = {frozenset(features) : states[transition[1]]}
            else:
                states[transition[0]].outputs[input][frozenset(features)] = output
                states[transition[0]].transitions[input][frozenset(features)] = states[transition[1]]
        
        
        
        return FFSM(all_states, initial_state, all_features)
        
    def __str__(self) -> str:
        output = ""
        for transition in self.transitions:
            output = output + transition.__str__()
        return output

    def __eq__(self, other) -> bool:
        if isinstance(other, FFSM):
            equal = True
            for current_state_1 in self.current_states:
                match_found = False
                for current_state_2 in other.current_states:
                    if current_state_1[0] == current_state_2[0] and current_state_1[1] == current_state_2[1]: #states are equal
                        match_found = True
                        break
                equal = equal and match_found
            return equal and self.alphabet == other.alphabet and self.features == other.features and self.initial_state == other.initial_state and self.states == other.states


    def step(self, input : str, features_in : set[str] = set()) -> list[(str, set[str])]:
        new_current_states = []
        outputs = []
        for current_state, feature_config in self.current_states:
            features = unify_features(feature_config, features_in)
            if len(features) > 0 or (features == [] and feature_config == []):
                transitions = current_state.transitions[input]
                for transition_features, new_state in transitions.items():
                    feature_config_transition = unify_features(features,transition_features)
                    if len(feature_config_transition) > 0:
                        new_current_states.append((new_state, feature_config_transition))
                        outputs.append((current_state.outputs[input][transition_features], feature_config_transition))                        
                        
        if new_current_states == []:
            raise Exception("Invalid input: ", input, " given the features: ", features)
        else:
            self.current_states = new_current_states
        return outputs

    def make_input_complete(self) -> None:
        for state in self.states:
            input_dict = {}
            for input in self.alphabet:
                input_dict[input] = set()
                if input in state.transitions.keys():
                    for features in state.transitions[input].keys():
                        input_dict[input] = input_dict[input].union(features)

            for input, features in input_dict.items():
                feature_diff = state.features.difference(features)
                if len(feature_diff) > 0:
                    if input not in state.transitions.keys():
                        state.transitions[input] = {frozenset(feature_diff) : state}
                        state.outputs[input] = {frozenset(feature_diff) : 'epsilon'}
                    else:
                        state.transitions[input][frozenset(feature_diff)] = state
                        state.outputs[input][frozenset(feature_diff)] = 'epsilon'
                        

    def reset_when_sink(self):
        for feature in self.features:
            for state in self.states:
                if feature in state.features:
                    is_sink = True
                    for edge_dict in state.transitions.values():
                        for features, to_state in edge_dict.items():
                            if feature in features and to_state != state:
                                is_sink = False
                                break
                    if is_sink:
                        self.alphabet.add(RESET_IN)
                        if RESET_IN not in state.transitions.keys():
                            state.transitions[RESET_IN] = {frozenset({feature}) : self.initial_state}
                            state.outputs[RESET_IN] = {frozenset({feature}) : RESET_OUT}
                        else:
                            state.transitions[RESET_IN][frozenset({feature})] = self.initial_state
                            state.outputs[RESET_IN][frozenset({feature})] = RESET_OUT


    def reset_to_initial_state(self) -> None:
        self.current_states = [(self.initial_state, self.features)]


