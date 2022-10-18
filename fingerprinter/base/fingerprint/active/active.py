import networkx as nx
import random

from aalpy.SULs.AutomataSUL import MealySUL
from base.fingerprint.active.HDT import HDT


class Simulator:
    
    def __init__(self, hdt : HDT) -> None:
        self.hdt = hdt

        
    def _do_random_input(self, current_state : str, sul : MealySUL) -> set[str]:
        current_features = self.hdt.ffsm.features
        initial_state = current_state
        edges = self.hdt.graph.out_edges(current_state,data=True)
        total_queries = []
        while self.hdt.can_detect_change(current_features):
            input_output = []
            while list(edges) != [] and self.hdt.can_detect_change(current_features):
                edge = random.choice(list(edges))
                input = edge[2]["label"]
                try:
                    output = sul.step(input)
                    input_output.append((input,output))
                    out_edges = self.hdt.graph.out_edges(edge[1],data=True)
                    out_edge = None
                    for e in out_edges:
                        if e[2]["label"].replace(" ", "") == str(output):
                            out_edge = e
                            break
                    current_state = out_edge[1]
                    diff_features = current_features.difference(out_edge[2]["variant"])
                    
                    if len(diff_features) > 0:
                        self.hdt.remove_features_graph(diff_features)
                    current_features = current_features - diff_features
                except Exception as e:
                    
                    invalid_edges = self.hdt.graph.out_edges(edge[1], data=True)
                    invalid_features = set()
                    for inv_edge in invalid_edges:
                        invalid_features = invalid_features.union(inv_edge[2]["variant"])
                    current_features = current_features.difference(invalid_features)
                    self.hdt.remove_features_graph(invalid_features)
                edges = self.hdt.graph.out_edges(current_state,data=True)
            
            total_queries = total_queries + input_output
            self.hdt.remove_trace(initial_state,input_output)
            input_output.clear()
            sul.pre()
            current_state = initial_state
            edges = self.hdt.graph.out_edges(current_state,data=True)
        print(total_queries)
        return current_features

    def _shortest_path_fingerprinting(self, current_state : str, sul : MealySUL) -> set[str]:
        current_features = self.hdt.ffsm.features
        initial_state = current_state
        self.total_queries = []
        self.number_of_reset = 0
        while True:
            inputs = self.hdt.shortest_distinguishing_information(current_features, current_state)
            while inputs != []:
                for input in inputs:
                    self.total_queries.append(input)
                    try:
                        output = sul.step(input)
                        current_state, features = self.hdt.step(current_state,input,str(output))
                        invalid_features = current_features.difference(features)
                        current_features = features
                        if len(invalid_features) > 0:
                            self.hdt.remove_features_graph(invalid_features)
                    except Exception as e:
                        invalid_features = self.hdt.get_possible_features_input(current_state,input)
                        current_features = current_features.difference(invalid_features)
                        self.hdt.remove_features_graph(invalid_features)
                inputs = self.hdt.shortest_distinguishing_information(current_features, current_state)

            if self.hdt.can_detect_change(current_features):
                self.number_of_reset = self.number_of_reset + 1
                sul.pre()
                current_state = initial_state
            else:
                break
        print(self.total_queries, self.number_of_reset)
        return current_features

    def fingerprint_system(self, sul : MealySUL) -> set[str]:
        nx.drawing.nx_agraph.write_dot(self.hdt.graph,"test.dot")
        # features = self._do_random_input(self.hdt.root,sul)
        features = self._shortest_path_fingerprinting(self.hdt.root, sul)
        return features


