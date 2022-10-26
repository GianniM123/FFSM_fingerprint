from dataclasses import dataclass
import copy
import string
from collections import deque
 
import networkx as nx

from base.FFSM.FFSM import FFSM,  unify_features


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
    features: set[str]
    ffsm: FFSM
    sequence : list[tuple[str,str]]
    pre: 'Option'

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


class CADS:

    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm
        self.ads = None
        self._calculate_graph()
    
    def _calculate_graph(self) -> None:
        graph = nx.DiGraph()
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(self.ffsm.features,copy.deepcopy(self.ffsm), [], None)
        
        options = deque()
        options.append(root)
        names = []
        while len(options) > 0:
            to_discover = options.pop()
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                graph.add_node(id, label=str(to_discover.features), inputs={})
                for input, output in to_discover.sequence:
                    graph.nodes[id]["inputs"][input] = output
            else:
                graph.nodes[id]["inputs"][to_discover.sequence[-1][0]] = to_discover.sequence[-1][1]
            
            if to_discover.pre != None:
                node_id = id_in_list(to_discover.pre,names)
                if node_id is None:
                    node_id = fresh_var(len(names))
                    names.append((to_discover.pre, node_id))
                    graph.add_node(node_id, label=str(to_discover.pre.features), inputs={})
                
                if graph.out_degree(node_id) >= 1:
                    edges = copy.deepcopy(graph.out_edges(node_id,data=True))
                    to_remove = []
                    for e in edges:
                        if to_discover.sequence[-1][0] in graph.nodes[e[1]]["inputs"].keys():
                            graph.add_edge(e[0],e[1], label=to_discover.sequence[-1][0] + "/" + graph.nodes[e[1]]["inputs"][to_discover.sequence[-1][0]], input=to_discover.sequence[-1][0] )
                        else:
                            to_remove.append(e)
                    for e in to_remove:
                        graph.remove_edge(e[0],e[1])
                
                graph.add_edge(node_id,id, label=to_discover.sequence[-1][0] + "/" + to_discover.sequence[-1][1], input=to_discover.sequence[-1][0])


            seen_states.append(to_discover)
            for input in self._best_input(to_discover.ffsm):
                try:
                    new_ffsm = copy.deepcopy(to_discover.ffsm)
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
                    done = False
                    for output, features  in output_dict.items():
                        step_ffsm = copy.deepcopy(to_discover.ffsm)
                        step_ffsm.step(input,features)
                        new_option = Option(features,step_ffsm, to_discover.sequence + [(input,output)], to_discover)
                        
                        if len(new_option.features) == 1:
                            done = True
                            seen_states.append(new_option)
                            node_id = id_in_list(new_option,names)
                            if node_id is None:
                                node_id = fresh_var(len(names))
                                names.append((new_option, node_id))
                                graph.add_node(node_id, label=str(new_option.features), inputs={input:output})
                                graph.add_edge(id,node_id, label=input + "/" + output, input=input)
                            else:
                                graph.nodes[node_id]["inputs"][input] = output

                            filtered = list(filter(lambda x: len(x.features) == 1, seen_states))
                            just_features = [list(x.features)[0] for x in filtered]
                            
                            for f1 in self.ffsm.features:
                                if f1 not in just_features:
                                    done = False
                                    break
                            if done:
                                for x in filtered:
                                    print(x.features, " ", x.sequence)
                                options = []
                                break
                        elif new_option not in seen_states and new_option not in options:
                            options.append(new_option)
                    if done:
                        break

                        
                        
                except Exception as e:
                    print(e)
                    pass

        self.graph = graph
        nx.drawing.nx_agraph.write_dot(self.graph,"test.dot")

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
        for input, edge_infos in input_edges_dict.items():
            outputs = []
            states = []
            for output, state in edge_infos:
                if output not in outputs:
                    outputs.append(output)
                if state not in states:
                    states.append(state)
            if len(outputs) > 1:
                rank_best_inputs.append(input)
            elif len(states) > 1 and len(rank_best_inputs) >= 1:
                rank_best_inputs.insert(len(rank_best_inputs)-1,input)
            else:
                rank_best_inputs.insert(0,input) 
        return rank_best_inputs        


        

