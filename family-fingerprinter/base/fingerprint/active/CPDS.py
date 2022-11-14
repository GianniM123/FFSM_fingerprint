from dataclasses import dataclass
import copy
import string

import networkx as nx

from base.FFSM.FFSM import FFSM
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence, id_in_list, fresh_var



@dataclass
class Option:
    features: list[set[str]]
    ffsm: FFSM
    sequence : list[tuple[set[str],list[tuple[str,str]]]]

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
            self.features.sort()
            other.features.sort()
            return (self.features == other.features and equal) 


class CPDS(ConfigurationDistinguishingSequence):

    def __init__(self, ffsm: FFSM) -> None:
        super().__init__(ffsm)
    
    def _calculate_graph(self):
        self.graph = nx.Graph()
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(list(self.ffsm.features),copy.deepcopy(self.ffsm), [(self.ffsm.features, [])])
        nr_features = len(self.ffsm.features)
        options = [root]
        names = []
        while len(options) > 0:
            to_discover = options.pop(0)
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                self.graph.add_node(id, label=to_discover.features)
            
            seen_states.append(to_discover)
            for input in to_discover.ffsm.alphabet:
                try:
                    new_ffsm = copy.deepcopy(to_discover.ffsm)
                    outputs = new_ffsm.step(input)
                    output_dict : dict[str, set] = {}
                    
                    count_features = 0
                    for out, features in outputs:
                        count_features = count_features + len(features)
                        if out not in output_dict.keys():
                            output_dict[out] = set(features)
                            
                        else:
                            output_dict[out] = output_dict[out].union(set(features))
                    if count_features != nr_features:
                        continue
                    new_option = Option([],new_ffsm, []) 
                    for output, new_split_features in output_dict.items():
                        for splitted_features, sequence in to_discover.sequence:
                            features_intersection = new_split_features.intersection(splitted_features)
                            if len(features_intersection) > 0:
                                new_option.features.append(features_intersection)
                                new_option.sequence.append((features_intersection, sequence + [(input,output)]))

                    node_id = id_in_list(new_option,names)
                    if node_id is None:
                        node_id = fresh_var(len(names))
                        names.append((new_option, node_id))
                        self.graph.add_node(node_id, label=new_option.features)
                        self.graph.add_edge(id,node_id, label=input)
                        options.append(new_option)
                    
                        stop = True
                        for f in new_option.features:
                            stop = stop and len(f) == 1 
                        if stop:
                            options = []
                            self.exists = True
                            
                            self.configuration_ss = nx.MultiDiGraph()
                            self.root = "a"
                            self.configuration_ss.add_node(self.root, label=self.ffsm.features)
                            count = 0
                            for configuration, sequence in new_option.sequence:
                                current_node = self.root
                                for input, output in sequence:
                                    label = input + "/" + output
                                    to_node = None
                                    for edge in self.configuration_ss.out_edges(current_node, data=True):
                                        if edge[2]["label"] == label:
                                            to_node = edge[1]
                                            break
                                    if to_node is not None:
                                        self.configuration_ss.nodes[to_node]["label"] = self.configuration_ss.nodes[to_node]["label"].union(configuration)
                                        current_node = to_node
                                    else:
                                        self.configuration_ss.add_node(self.root + str(count),label=configuration)
                                        self.configuration_ss.add_edge(current_node, self.root + str(count), label=label)
                                        current_node = self.root + str(count)
                                        count = count + 1
                            
                            break
                except Exception as e:
                    print(e)
                    pass
        