from dataclasses import dataclass
import copy
import string
from time import sleep
import networkx as nx
import random

from aalpy.SULs.AutomataSUL import MealySUL
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

def remove_cycles(graph: nx.MultiDiGraph, current_node : str, seen_nodes : list[str] = []):
    edges = graph.out_edges(current_node)
    to_remove_edge = []
    to_remove_node = []
    seen_nodes.append(current_node)
    for edge in edges:
        to_nodes = graph.out_edges(edge[1])
        add_edge_to_remove = False
        for node in to_nodes:
            if node[1] not in seen_nodes:
                seen_nodes_cp = copy.deepcopy(seen_nodes)
                remove_cycles(graph,node[1],seen_nodes_cp)
            else:
                to_remove_edge.append(node)
                add_edge_to_remove = True
        if add_edge_to_remove:
            to_remove_edge.append(edge)
            to_remove_node.append(edge[1])
    
    for remove in to_remove_edge:
        graph.remove_edge(remove[0],remove[1])
    for remove in to_remove_node:
        graph.remove_node(remove)
    
        


@dataclass
class Option:
    features: set[str]
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
            return self.features == other.features and len(current_state_1) == len(current_state_2) and equal



class Simulator:
    
    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm

    def _calculate_graph(self) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
        self.ffsm.reset_to_initial_state()
        seen_states = []
        root = Option(self.ffsm.features,copy.deepcopy(self.ffsm), [])
        options = [root]
        names = []
        while len(options) > 0:
            to_discover = options[0]
            id = id_in_list(to_discover,names)
            if id == None:
                id = fresh_var(len(names))
                names.append((to_discover, id))
                graph.add_node(id, label=str(to_discover.features), variant=to_discover.features)
            
            options.pop(0)
            seen_states.append(to_discover)
            counter = 0
            for input in to_discover.ffsm.alphabet:
                new_ffsm = copy.deepcopy(to_discover.ffsm)
                outputs = new_ffsm.step(input)
                output_dict = {}
                
                node_added = False
                for out, features in outputs:
                    if out not in output_dict.keys():
                        output_dict[out] = set(features)
                    else:
                        output_dict[out] = output_dict[out].union(set(features)) 
                for key, value in output_dict.items():
                    node_ffsm = copy.deepcopy(to_discover.ffsm)
                    node_ffsm.step(input, list(value))
                    node_option = Option(value, node_ffsm,to_discover.sequence + [(input, key)])
                    node_id = id_in_list(node_option,names)
                    if node_id == None:
                        node_id = fresh_var(len(names))
                        names.append((node_option,node_id))
                        graph.add_node(node_id, label=str(node_option.features), variant=node_option.features)
                    if id != node_id and node_option != root :
                        graph.add_edge(id + str(counter), node_id, label=key, variant=node_option.features)
                        node_added = True
                    if len(value) == 1:
                        seen_states.append(node_option)
                    else:
                        if node_option not in options and node_option not in seen_states:
                            options.append(node_option)
                if node_added:
                    graph.add_node(id + str(counter), label="")
                    graph.add_edge(id,id + str(counter), label=input)
                counter = counter + 1
                
        possible_fingerprint = filter(lambda x : len(x.features) == 1, seen_states)
        nodes_pair = [ (frozenset(i.features),id_in_list(i,names)) for i in possible_fingerprint ]
        nodes_pair = set(nodes_pair)
        # if the input contains a cycle, the HDG (heuristic decision graph) contains a cycle
        # if the input is cycle free, the HDG is cycle free

        # it is given that if there is a node for all single features in the model, there also
        # exists a path which traverses them, otherwise it wasn't possible to split the features
        # paths = {}
        # for i in nodes_pair:
        #     if i[0] not in paths.keys():
        #         paths[i[0]] = list(nx.algorithms.all_simple_paths(graph,id_in_list(root,names),i[1]))
        #     else:
        #         paths[i[0]] = paths[i[0]] + list(nx.algorithms.all_simple_paths(graph,id_in_list(root,names),i[1]))
        # for key, value in paths.items():
        #     print(key)
        #     for v in value:
        #         print(v)
        print(nx.algorithms.is_directed_acyclic_graph(graph))
        nx.drawing.nx_agraph.write_dot(graph,"test.dot")
        return graph
    
    def _remove_features_graph(self, graph : nx.MultiDiGraph, features : set[str]):
        to_remove_node = []
        for node in graph.nodes.data():
            if "variant" in node[1].keys():
                new_features = node[1]["variant"].difference(features)
                if len(new_features) == 0:
                    to_remove_node.append(node[0])
                else:
                    node[1]["variant"] = new_features
                    node[1]["label"] = new_features
        
        to_remove_edge = []
        for edge in graph.edges.data():
            if "variant" in edge[2].keys():
                new_features = edge[2]["variant"].difference(features)
                if len(new_features) == 0:
                    to_remove_edge.append(edge)
                else:
                    edge[2]["variant"] = new_features
        
        for edge in to_remove_edge:
            node = edge[0]
            graph.remove_edge(edge[0], edge[1])
            out_edges = graph.out_edges(node)
            if(len(out_edges) == 0):
                in_edge = copy.deepcopy(graph.in_edges(node))
                for e in in_edge:
                    graph.remove_edge(e[0],e[1])
                if node not in to_remove_node:
                    to_remove_node.append(node)

        for node in to_remove_node:
            graph.remove_node(node)
        

    def _can_detect_change(self, graph : nx.MultiGraph, current_features : set[str]) -> bool:
        for node in graph.nodes.data():
            if "variant" in node[1].keys():
                if current_features != node[1]["variant"]:
                    return True
        for edge in graph.edges.data():
            if "variant" in edge[2].keys():
                if current_features != edge[2]["variant"]:
                    return True
        return False        


    def _do_random_input(self, graph: nx.MultiDiGraph, current_state : str, sul : MealySUL) -> list[str]:
        current_features = self.ffsm.features

    
        edges = graph.out_edges(current_state,data=True)
        while self._can_detect_change(graph,current_features):
            input_output = []
            while list(edges) != []:
                edge = random.choice(list(edges))
                input = edge[2]["label"]
                try:
                    # print(input)
                    output = sul.step(input)
                    # print(output)
                    input_output.append((input,output))
                    out_edges = graph.out_edges(edge[1],data=True)
                    out_edge = None
                    for e in out_edges:
                        if e[2]["label"].replace(" ", "") == output:
                            out_edge = e
                            break
                    current_state = out_edge[1]
                    diff_features = current_features.difference(out_edge[2]["variant"])
                    
                    if len(diff_features) > 0:
                        self._remove_features_graph(graph,diff_features)
                    current_features = current_features - diff_features
                except Exception as e:
                    invalid_edges = graph.out_edges(edge[1], data=True)
                    invalid_features = set()
                    for inv_edge in invalid_edges:
                        invalid_features = invalid_features.union(inv_edge[2]["variant"])
                    current_features = current_features.difference(invalid_features)
                    self._remove_features_graph(graph,invalid_features)
                edges = graph.out_edges(current_state,data=True)
            
            sul.pre()
            current_state = 'a'
            edges = graph.out_edges(current_state,data=True)
        return current_features


    def fingerprint_system(self, sul : MealySUL) -> str:
        graph = self._calculate_graph()
        features = self._do_random_input(graph,'a',sul)
        print("res: ", features)
        nx.drawing.nx_agraph.write_dot(graph,"test.dot")

