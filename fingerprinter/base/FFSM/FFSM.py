import networkx as nx

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
    
    def __init__(self, transitions: list[ConditionalTransition]):
        self.transitions = transitions

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
        
        transitions = []
        for transition in ffsm.edges.data():
            in_output = transition[2]["label"].split("/")
            features = transition[2]["feature"].split("|")
            transitions.append(ConditionalTransition(states[transition[0]], states[transition[1]], in_output[0], in_output[1],features))

        
        return FFSM(transitions)
        
    def __str__(self) -> str:
        output = ""
        for transition in self.transitions:
            output = output + transition.__str__()
        return output


    def incoming_transitions_of(self, state : ConditionalState):
        incoming_transitions = []
        for transition in self.transitions:
            if transition.to_state == state:
                incoming_transitions.append(transition)
        return incoming_transitions

    def outgoing_transitions_of(self, state : ConditionalState):
        outgoing_transitions = []
        for transition in self.transitions:
            if transition.from_state == state:
                outgoing_transitions.append(transition)
        return outgoing_transitions
