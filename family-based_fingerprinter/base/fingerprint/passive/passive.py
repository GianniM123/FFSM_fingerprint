from base.FFSM.FFSM import FFSM, unify_configs, ConditionalState



def trace_fingerprinting(ffsm : FFSM, trace : list[(str,str)], only_initial_state = False) -> set[str]:
    uncertainty : list[tuple[ConditionalState,set[str]]] = []
    if only_initial_state:
        uncertainty.append((ffsm.initial_state.state_id,ffsm.initial_state.features))
    else:
        for s in ffsm.states:
            uncertainty.append((s.state_id, s.features))
    trace_id = 0
    transitions = ffsm.get_transitions()
    while uncertainty != [] and trace_id < len(trace):
        new_uncertainty = []
        for from_state, to_state, input, output in transitions:
            for current_state_id, current_features in uncertainty:
               if from_state[0] == current_state_id and input[0] == trace[trace_id][0] and output == trace[trace_id][1]:
                    new_configs = unify_configs(current_features,input[1])
                    if len(new_configs) > 0:
                        new_uncertainty.append((to_state[0],new_configs))               
            
        uncertainty = new_uncertainty
        trace_id = trace_id + 1
    
    possible_features = set()
    for _, feature in uncertainty:
        possible_features = possible_features.union(feature)
    return possible_features