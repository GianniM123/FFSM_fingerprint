import networkx as nx

def unify_features(current_variants : list[str], new_variants : list[str]):
    if current_variants == []:
        return new_variants
    elif new_variants == []:
        return current_variants
    
    equal_variants = []
    for current_variant in current_variants:
        for new_variant in new_variants:
            if current_variant == new_variant:
                equal_variants.append(current_variant)
                break

    return equal_variants

class ConditionalState():
    
    def __init__(self, state_id : str, features : list[str]):
        self.state_id = state_id
        self.features = features

    def __eq__(self, other) -> bool:
        if isinstance(other,ConditionalState):
            return self.state_id == other.state_id
        return False
    
    def __str__(self) -> str:
        return "(" + self.state_id + ", " + self.features.__str__() + ")"


class ConditionalTransition():

    def __init__(self, from_state: ConditionalState, to_state: ConditionalState, input : str, output : str, features : list[str]):
        self.from_state = from_state
        self.to_state = to_state
        self.input = input
        self.output = output
        self.features = features
    
    def __str__(self) -> str:
        return "(" + self.from_state.__str__() + ", " + self.to_state.__str__() + ", " + self.input + "/" + self.output + ", " + self.features.__str__() + ")"
        

class FFSM():
    
    def __init__(self, transitions: list[ConditionalTransition], initial_state: ConditionalState):
        self.transitions = transitions
        self.initial_state = initial_state
        self.current_states = [(initial_state, [])]

        self.states = []
        for transition in self.transitions:
            if transition.from_state not in self.states:
                self.states.append(transition.from_state)
            if transition.to_state not in self.states:
                self.states.append(transition.to_state)        

    @classmethod
    def from_file(self, file: str):
        ffsm = nx.drawing.nx_agraph.read_dot(file)

        states = {}
        for state in ffsm.nodes.data():
            features = state[1]["feature"].split("|")
            if features[0] == "True":
                features = []
            states[state[0]] = ConditionalState(state[0],features)
        
        initial_state = None
        transitions = []
        for transition in ffsm.edges.data():
            if transition[0] == "__start0":
                initial_state = states[transition[1]]
                continue
            in_output = transition[2]["label"].split("/")
            features = transition[2]["feature"].split("|")
            transitions.append(ConditionalTransition(states[transition[0]], states[transition[1]], in_output[0], in_output[1],features))
        return FFSM(transitions, initial_state)
        
    def __str__(self) -> str:
        output = ""
        for transition in self.transitions:
            output = output + transition.__str__()
        return output

    def step(self, input : str, features : list[str]) -> list[(str, list[str])]:
        new_current_states = []
        outputs = []
        for current_state, feature_config in self.current_states:
            if len(unify_features(feature_config, features)) > 0 or (features == [] and feature_config == []):
                transitions = self.outgoing_transitions_of(current_state)
                for transition in transitions:
                    feature_config_transition = unify_features(features,transition.features)
                    if transition.input == input and len(feature_config_transition) > 0:
                        new_current_states.append((transition.to_state, feature_config_transition))
                        outputs.append((transition.output, feature_config_transition))
        if new_current_states == []:
            raise Exception("Invalid input: ", input, " given the features: ", features)
        else:
            self.current_states = new_current_states
        return outputs


    def incoming_transitions_of(self, state : ConditionalState) -> list[ConditionalTransition]:
        incoming_transitions = []
        for transition in self.transitions:
            if transition.to_state == state:
                incoming_transitions.append(transition)
        return incoming_transitions

    def outgoing_transitions_of(self, state : ConditionalState) -> list[ConditionalTransition]:
        outgoing_transitions = []
        for transition in self.transitions:
            if transition.from_state == state:
                outgoing_transitions.append(transition)
        return outgoing_transitions
