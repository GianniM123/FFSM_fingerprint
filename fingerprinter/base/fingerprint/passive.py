from base.FFSM.FFSM import FFSM


def unify_features(current_variants : list[str], new_variants : list[str]):
    if current_variants == []:
        return new_variants
    elif new_variants == []:
        return current_variants
    
    current = set(current_variants)
    new = set(new_variants)

    if new.issubset(current):
        return new_variants
    elif current.issubset(new):
        return current_variants
    
    return []



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
                        pair = (transition.to_state.state_id, features_config)
                        if pair not in new_uncertainty: # list is not a hashable type, therefore can't use set
                            new_uncertainty.append(pair)
        uncertainty = new_uncertainty
        trace_id = trace_id + 1
    
    possible_features = set()
    for s, feature in uncertainty:
        for f in feature:
            possible_features.add(f)
    return possible_features