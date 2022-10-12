from dataclasses import dataclass
import copy
import string
import networkx as nx

from aalpy.SULs.AutomataSUL import MealySUL
from base.FFSM.FFSM import FFSM


def fresh_var(index):
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
    features: list[str]
    ffsm: FFSM
    sequence: list[tuple[str,str]]

    def __eq__(self, other) -> bool:
        if isinstance(other, Option):
            equal = True
            for current_state_1 in self.ffsm.current_states:
                match_found = False
                for current_state_2 in other.ffsm.current_states:
                    current_state_1[1].sort() 
                    current_state_2[1].sort()
                    if current_state_1[0] == current_state_2[0] and current_state_1[1] == current_state_2[1]: #states are equal
                        match_found = True
                        break
                equal = equal and match_found
            self.features.sort()
            other.features.sort()
            return self.features == other.features and len(current_state_1) == len(current_state_2) and equal



class Simulator:
    
    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm

    def _calculate_graph(self):
        graph = nx.MultiDiGraph()
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(list(self.ffsm.features),copy.deepcopy(self.ffsm), [])
        options = [root]
        names = []
        while len(options) > 0:
            to_discover = options[0]
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                graph.add_node(id, label=str(to_discover.features))
            
            options.pop(0)
            seen_states.append(to_discover)
            counter = 0
            for input in to_discover.ffsm.alphabet:
                new_ffsm = copy.deepcopy(to_discover.ffsm)
                outputs = new_ffsm.step(input)
                output_dict = {}
                graph.add_node(id + str(counter), label="")
                graph.add_edge(id,id + str(counter), label=input)
                for out, features in outputs:
                    if out not in output_dict.keys():
                        output_dict[out] = set(features)
                    else:
                        output_dict[out] = output_dict[out].union(set(features)) 
                for key, value in output_dict.items():
                    node_ffsm = copy.deepcopy(to_discover.ffsm)
                    node_ffsm.step(input, list(value))
                    node_option = Option(list(value), node_ffsm,to_discover.sequence + [(input, key)])
                    node_id = id_in_list(node_option,names)
                    if node_id == None:
                        node_id = fresh_var(len(names))
                        names.append((node_option,node_id))
                        graph.add_node(node_id, label=str(node_option.features))
                    graph.add_edge(id + str(counter), node_id, label=key)
                    if len(value) == 1:
                        seen_states.append(node_option)
                    else:
                        if node_option not in options and node_option not in seen_states:
                            options.append(node_option)
                counter = counter + 1
        possible_fingerprint = filter(lambda x : len(x.features) == 1, seen_states)
        for i in possible_fingerprint:
            print(i.features, " ", i.sequence)
        nx.drawing.nx_agraph.write_dot(graph,"test.dot")
    
    
    def fingerprint_system(self, sul : MealySUL) -> str:
        graph = self._calculate_graph()

