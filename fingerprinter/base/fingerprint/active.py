from dataclasses import dataclass
import copy

from aalpy.SULs.AutomataSUL import MealySUL
from base.FFSM.FFSM import FFSM



@dataclass
class Option:
    features: list[str]
    ffsm: FFSM
    sequence: list[(str,str)]

    def __eq__(self, other) -> bool:
        if isinstance(other, Option):
            equal = True
            for current_state_1 in self.ffsm.current_states:
                match_found = False
                for current_state_2 in other.ffsm.current_states:
                    if current_state_1[0] == current_state_2[0] and current_state_1[1].sort() == current_state_2[1].sort(): #states are equal
                        match_found = True
                equal = equal and match_found

            return self.features.sort() == other.features.sort() and len(current_state_1) == len(current_state_2) and equal



class Simulator:
    
    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm

    def _calculate_graph(self):
        self.ffsm.reset_to_initial_state()
        seen_states = []
        options = [Option(list(self.ffsm.features),copy.deepcopy(self.ffsm), [])]
        while len(options) > 0:
            options.sort(key=lambda x : len(x.features))
            to_discover = options[0]
            options.pop(0)
            seen_states.append(to_discover)
            for input in to_discover.ffsm.alphabet:
                new_ffsm = copy.deepcopy(to_discover.ffsm)
                outputs = new_ffsm.step(input)
                output_dict = {}
                for out, features in outputs:
                    if out not in output_dict.keys():
                        output_dict[out] = set(features)
                    else:
                        output_dict[out] = output_dict[out].union(set(features)) 
                for key, value in output_dict.items():
                    node_ffsm = copy.deepcopy(to_discover.ffsm)
                    node_ffsm.step(input, list(value))
                    node_option = Option(list(value), node_ffsm,to_discover.sequence + [(input, key)])
                    if len(value) == 1:
                        seen_states.append(node_option)
                    else:
                        if node_option not in options and node_option not in seen_states:
                            options.append(node_option)
        possible_fingerprint = filter(lambda x : len(x.features) == 1, seen_states)
        for i in possible_fingerprint:
            print(i.features, " ", i.sequence)
            
    
    
    def fingerprint_system(self, sul : MealySUL) -> str:
        graph = self._calculate_graph()

