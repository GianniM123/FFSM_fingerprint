from base.FFSM.FFSM import FFSM, ConditionalState


def feature_selection(current_features : list[str], new_features : list[str]):
    if current_features == []:
        return new_features
    
    current = set(current_features)
    new = set(new_features)

    if new.issubset(current):
        return new_features


    for feature in current_features:
        if feature not in new_features:
            return []
    return current_features



def trace_fingerprinting(ffsm : FFSM, trace : list[(str,str)]):
    states = list(ffsm.states)

    features = []
    for s in states:
        features.append((s.state_id, s.features))

    for input, output in trace:
        new_states = []
        for state, feature_con in features:
            transitions = ffsm.outgoing_transitions_of(ConditionalState(state,[]))
            for transition in transitions:
                if transition.input == input and transition.output == output:
                    # check if the features are confirm
                    features_config = feature_selection(feature_con, transition.features)
                    if len(features_config) > 0:
                        new_states.append((transition.to_state.state_id, features_config))
        features = new_states
    
    possible_features = set()
    for s, feature in features:
        for f in feature:
            possible_features.add(f)
    return possible_features