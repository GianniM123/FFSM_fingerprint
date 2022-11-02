from dataclasses import dataclass
import copy
import string
 
import networkx as nx

from base.FFSM.FFSM import FFSM,  unify_features
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence, id_in_list, fresh_var



@dataclass
class Option:
    features: set[str]
    ffsm: FFSM
    graph : nx.MultiDiGraph

    def __eq__(self, other) -> bool:
        if isinstance(other, Option):
            equal = True
            for current_state_1 in self.ffsm.current_states:
                match_found = False
                for current_state_2 in other.ffsm.current_states:
                    if current_state_1[0] == current_state_2[0] and current_state_1[1] == current_state_2[1]: #states are equal
                        match_found = True
                        break
                equal = equal and match_found
            return (self.features == other.features and equal) 


class CADS(ConfigurationDistinguishingSequence):

    def __init__(self, ffsm: FFSM) -> None:
        super().__init__(ffsm)
    
    def _calculate_graph(self):
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(self.ffsm.features,copy.deepcopy(self.ffsm), nx.MultiDiGraph())

        options : list[Option] = []
        options.append(root)
        names = []

        self.root = fresh_var(len(names))
        names.append((root, self.root))
        root.graph.add_node(self.root, label=root.features)
        while len(options) > 0:
            to_discover = options.pop(0)
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                to_discover.graph.add_node(id, label=to_discover.features)
            elif not to_discover.graph.has_node(id):
                to_discover.graph.add_node(id, label=to_discover.features)
            
            seen_states.append(to_discover)
            # for input in self.ffsm.alphabet:
            for input in self._best_input(to_discover.ffsm):
                try:
                    new_ffsm = copy.deepcopy(to_discover.ffsm)
                    new_graph = copy.deepcopy(to_discover.graph)
                    outputs = new_ffsm.step(input)
                    output_dict : dict[str, set] = {}
                    counter = 0
                    for out, features in outputs:
                        counter = counter + len(features)
                        if out not in output_dict.keys():
                            output_dict[out] = set(features)
                            
                        else:
                            output_dict[out] = output_dict[out].union(set(features))
                    if counter != len(to_discover.features):
                        continue
                    for output, features  in output_dict.items():
                        step_ffsm = copy.deepcopy(to_discover.ffsm)
                        step_ffsm.step(input,features)
                        new_option = Option(features,step_ffsm, new_graph)

                        node_id = id_in_list(new_option,names)
                        if node_id is None:
                            node_id = fresh_var(len(names))
                            names.append((new_option, node_id))
                            new_option.graph.add_node(node_id, label=new_option.features)
                        elif not new_option.graph.has_node(node_id):
                            new_option.graph.add_node(node_id, label=new_option.features)
                        if node_id != id:
                            new_option.graph.add_edge(id,node_id, label=input + "/" + output)

                        if len(new_option.features) == 1:
                            seen_states.append(new_option)
                            filtered = list(filter(lambda x: len(x[1]["label"]) == 1, new_option.graph.nodes.data()))
                            just_features = set([list(x[1]["label"])[0] for x in filtered])
                            self.exists = True
                            for f1 in self.ffsm.features:
                                if f1 not in just_features:
                                    self.exists = False
                                    break
                            if self.exists:
                                self.configuration_ss = new_option.graph

                        elif new_option not in seen_states and new_option not in options:
                            options.append(new_option)
                    if self.exists:
                        options = []
                        break

                except Exception as e:
                    print(e)
                    pass
        
        

    def _best_input(self, ffsm : FFSM):
        edges = []
        for state, features in ffsm.current_states:
            edge = ffsm.outgoing_transitions_of(state)
            for e in edge:
                if len(unify_features(features,e.features)) > 0:
                    edges.append(e)
        
        input_edges_dict = {}
        for edge in edges:
            if edge.input not in input_edges_dict.keys():
                input_edges_dict[edge.input] = [(edge.output, edge.to_state)]
            else:
                input_edges_dict[edge.input] = input_edges_dict[edge.input] + [(edge.output, edge.to_state)]

        rank_best_inputs = []
        counter = 0
        for input, edge_infos in input_edges_dict.items():
            outputs = []
            states = []
            for output, state in edge_infos:
                if output not in outputs:
                    outputs.append(output)
                if state not in states:
                    states.append(state)
            if len(outputs) > 1:
                rank_best_inputs.insert(0,input)
                counter = counter + 1
            elif len(states) > 1 and len(rank_best_inputs) >= 1:
                rank_best_inputs.insert(counter,input)
            else:
                rank_best_inputs.append(input) 
        return rank_best_inputs        

