from dataclasses import dataclass
import copy
import string

import networkx as nx

from base.FFSM.FFSM import FFSM


def fresh_var(index : int):
    '''Generate a fresh variable on basis of the given index'''
    letters = string.ascii_lowercase
    value = 1
    if index >= len(letters):
        value = int(index / len(letters)) + 1
        index = index % len(letters)
    return letters[index] * value

def id_in_list(id, list):
    for ids in list:
        if ids[0] == id:
            return ids[1]
    return None


@dataclass
class Option:
    features: set[frozenset[str]]
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
            return (self.features == other.features and equal) 


class PDS:

    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm
        self.pds = None
        self._calculate_graph()
    
    def _calculate_graph(self) -> None:
        graph = nx.DiGraph()
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(set(frozenset(self.ffsm.features)),copy.deepcopy(self.ffsm), [(self.ffsm.features, [])])
        nr_features = len(self.ffsm.features)
        options = [root]
        names = []
        while len(options) > 0:
            to_discover = options.pop(0)
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                graph.add_node(id, label=to_discover.features)
            
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
                    new_option = Option(set(),new_ffsm, []) 
                    for output, new_split_features in output_dict.items():
                        for splitted_features, sequence in to_discover.sequence:
                            features_intersection = new_split_features.intersection(splitted_features)
                            if len(features_intersection) > 0:
                                new_option.features.add(frozenset(features_intersection))
                                new_option.sequence.append((features_intersection, sequence + [(input,output)]))

                    node_id = id_in_list(new_option,names)
                    if node_id is None:
                        node_id = fresh_var(len(names))
                        names.append((new_option, node_id))
                        graph.add_node(node_id, label=new_option.features)
                        graph.add_edge(id,node_id, label=input)
                        options.append(new_option)
                    
                        stop = True
                        for f in new_option.features:
                            stop = stop and len(f) == 1 
                        if stop:
                            options = []
                            self.pds = new_option.sequence
                            break
                except:
                    pass

        self.graph = graph
        nx.drawing.nx_agraph.write_dot(self.graph,"test.dot")