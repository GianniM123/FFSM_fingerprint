from dataclasses import dataclass
import copy

from aalpy.SULs.AutomataSUL import MealySUL
from base.FFSM.FFSM import FFSM



@dataclass
class Node:
    root: bool
    features: set[str]
    ffsm: FFSM
    childeren: dict[str,list[tuple[str,'Node']]]

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
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
            return (self.features == other.features) and (len(current_state_1) == len(current_state_2)) and equal
    
    def optimize(self, seen :list['Node'] = []) -> bool:
        if self not in seen:
            seen.append(self)
            to_remove_inputs = []
            for input, outputs in self.childeren.items():
                no_refinement = True
                for _, node in outputs:
                    can_be_removed = node.optimize(seen)
                    no_refinement = no_refinement and node.features == self.features and can_be_removed
                if no_refinement:
                    to_remove_inputs.append(input)
            for input in to_remove_inputs:
                self.childeren.pop(input)
        
            return self.childeren == {}
        return True
    
    def can_split_features(self, seen :list['Node'] = []) -> int:
        if self not in seen:
            seen.append(self)
            if self.childeren == {} and len(self.features) == 1:
                return 1
            elif self.childeren == {} and len(self.features) > 1:
                return -1
            else:
                lowest_inputs = -1
                for _, outputs in self.childeren.items():
                    total_inputs = 0
                    for _, node in outputs:
                        nr_inputs = node.can_split_features(seen)
                        if nr_inputs > 0:
                            total_inputs = total_inputs + nr_inputs + 1
                        else:
                            total_inputs = -1
                            break
                    if lowest_inputs == -1 or (lowest_inputs > total_inputs and total_inputs != -1):
                        lowest_inputs = total_inputs
                return lowest_inputs
        return 0

    def best_input(self) -> str:
        input_pair = ("",-1)
        for input, outputs in self.childeren.items():
            total_inputs = 0
            for _, node in outputs:
                nr_inputs = node.can_split_features([self])
                if nr_inputs > 0:
                    total_inputs = total_inputs + nr_inputs
                else:
                    total_inputs = -1
                    break
            print((input,total_inputs))
            if input_pair[1] == -1 or (input_pair[1] > total_inputs and total_inputs != -1):
                input_pair = (input,total_inputs)
        print("res: ", input_pair)
        


class Simulator:
    
    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm

    def _calculate_graph(self):
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Node(True,list(self.ffsm.features),copy.deepcopy(self.ffsm), {})
        options = [root]
        while len(options) > 0:
            to_discover = options[0]
            options.pop(0)
            seen_states.append(to_discover)
            for input in to_discover.ffsm.alphabet:
                new_ffsm = copy.deepcopy(to_discover.ffsm)
                try:
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
                        node_option = Node(False,value,node_ffsm, {})
                        if node_option in seen_states and node_option != to_discover:
                            index = seen_states.index(node_option)
                            if(seen_states[index].root == False):
                                node_option = seen_states[index]


                        if input in to_discover.childeren.keys():
                            to_discover.childeren[input].append((key,node_option))
                        else:
                            to_discover.childeren[input] = [(key,node_option)]
                        if len(value) == 1: # We don't need to continue searching if we have found a single variant
                            seen_states.append(node_option)
                        else:
                            if node_option not in options and node_option not in seen_states:
                                options.append(node_option)
                                
                except Exception as e:
                    print(e)
                    continue # current input not possible (can be due to being not input complete)
        
        root.optimize()
        root.best_input()

        # print()


            
    
    
    def fingerprint_system(self, sul : MealySUL) -> str:
        graph = self._calculate_graph()

