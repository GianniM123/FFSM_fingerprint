from base.FFSM.FFSM import FFSM, ConditionalState


def unify_features(current_features : list[str], new_features : list[str]):
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
    uncertainty = []
    for s in ffsm.states:
        uncertainty.append((s.state_id, s.features))

    trace_id = 0
    while uncertainty != [] and trace_id < len(trace):
        new_uncertainty = []
        for transition in ffsm.transitions:
            for state, feature_con in uncertainty:
                if transition.from_state.state_id == state and transition.input == trace[trace_id][0] and transition.output == trace[trace_id][1]:
                    # check if the features are confirm
                    features_config = unify_features(feature_con, transition.features)
                    if len(features_config) > 0:
                        new_uncertainty.append((transition.to_state.state_id, features_config))
        uncertainty = new_uncertainty
        trace_id = trace_id + 1
    
    possible_features = set()
    for s, feature in uncertainty:
        for f in feature:
            possible_features.add(f)
    return possible_features