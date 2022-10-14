import copy
import networkx as nx
import random

from aalpy.SULs.AutomataSUL import MealySUL
from base.fingerprint.HDT import HDT


class Simulator:
    
    def __init__(self, hdt : HDT) -> None:
        self.hdt = hdt

        
    def _do_random_input(self, current_state : str, sul : MealySUL) -> list[str]:
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


    def fingerprint_system(self, sul : MealySUL) -> str:
        nx.drawing.nx_agraph.write_dot(self.hdt.graph,"test.dot")
        # self.hdt.splitting_tree(self.hdt.ffsm.features)
        features = self._do_random_input('a',sul)
        print("res: ", features)

