from base.FFSM.FFSM import FFSM, unify_features



def trace_fingerprinting(ffsm : FFSM, trace : list[(str,str)], only_initial_state = False) -> set[str]:
    uncertainty = []
    if only_initial_state:
        uncertainty.append((ffsm.initial_state.state_id,ffsm.features))
    else:
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
                    pair = (transition.to_state.state_id, features_config)
                    if pair not in new_uncertainty: # list is not a hashable type, therefore can't use set
                        new_uncertainty.append(pair)
                            
        uncertainty = new_uncertainty
        trace_id = trace_id + 1
    
    possible_features = set()
    for _, feature in uncertainty:
        possible_features = possible_features.union(feature)
    return possible_features