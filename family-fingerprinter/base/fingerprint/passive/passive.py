from base.FFSM.FFSM import FFSM, unify_features, ConditionalState



def trace_fingerprinting(ffsm : FFSM, trace : list[(str,str)], only_initial_state = False) -> set[str]:
    uncertainty : list[tuple[ConditionalState,set[str]]] = []
    if only_initial_state:
        uncertainty.append((ffsm.initial_state,ffsm.initial_state.features))
    else:
        for s in ffsm.states:
            uncertainty.append((s, s.features))
    trace_id = 0
    while uncertainty != [] and trace_id < len(trace):
        new_uncertainty = []
        for current_state in uncertainty:
            trace_input = trace[trace_id][0]
            trace_output = trace[trace_id][1]

            ffsm.current_states = [current_state]
            outputs = ffsm.step(trace_input)
            for output in outputs:
                if output[0] == trace_output:
                    for new_current_state in ffsm.current_states:
                        if new_current_state not in new_uncertainty and len(unify_features(output[1],new_current_state[1])) > 0:
                            new_uncertainty.append(new_current_state)
                    break
                            
        uncertainty = new_uncertainty
        trace_id = trace_id + 1
    
    possible_features = set()
    for _, feature in uncertainty:
        possible_features = possible_features.union(feature)
    return possible_features