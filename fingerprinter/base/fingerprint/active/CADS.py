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
    sequence : list[str]

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
        root = Option(self.ffsm.features,copy.deepcopy(self.ffsm), [])

        options : list[Option] = []
        options.append(root)

        self.graph : nx.MultiDiGraph = nx.MultiDiGraph()
        self.root = fresh_var(0)
        self.graph.add_node(self.root, label=root.features)
        while len(options) > 0:
            to_discover = options.pop(0)
      
            seen_states.append(to_discover)
            for input in self.ffsm.alphabet:
            # for input in self._best_input(to_discover.ffsm):
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
                    for output, features  in output_dict.items():
                        step_ffsm = copy.deepcopy(to_discover.ffsm)
                        step_ffsm.step(input,features)
                        new_option = Option(features,step_ffsm, to_discover.sequence  + [input + "/" + output])

                        if len(new_option.features) == 1:
                            seen_states.append(new_option)

                            self._add_sequence_in_graph(new_option.sequence, new_option.features)

                            graph = copy.deepcopy(self.graph)
                            self._fix_graph()
                            if len(self.graph.nodes) > 1:
                                nx.drawing.nx_agraph.write_dot(self.graph, "test1.dot")
                                self.exists = True
                                self.configuration_ss = self.graph
                            else:
                                self.graph = graph

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

    def _add_sequence_in_graph(self, sequence, configuration):
        current_node = self.root
        
        for trace in sequence:
            edges = self.graph.out_edges(current_node, data=True)
            to_node = None
            for edge in edges:
                if edge[2]["label"] == trace:
                    to_node = edge[1]
                    break
            if to_node is not None:
                self.graph.nodes[to_node]["label"] = self.graph.nodes[to_node]["label"].union(configuration)
                current_node = to_node
            else:
                new_node = fresh_var(len(self.graph.nodes))
                self.graph.add_node(new_node,label=configuration)
                self.graph.add_edge(current_node, new_node, label=trace)
                current_node = new_node
    
    def _fix_graph(self):

        # Check if the property holds that for a input Parent is subset equal to children 
        for node in self.graph.nodes.data():
            input_dict = {}
            for edge in self.graph.out_edges(node[0], data=True):
                input = edge[2]["label"].split("/")[0]
                if input not in input_dict.keys():
                    input_dict[input] = self.graph.nodes[edge[1]]["label"]
                else:
                    input_dict[input] = input_dict[input].union(self.graph.nodes[edge[1]]["label"])

            all_edges = copy.deepcopy(self.graph.out_edges(node[0], keys=True, data=True))
            for input, feature_set in input_dict.items():
                if feature_set != node[1]["label"] or found:
                    for edge in all_edges:
                        if input == edge[3]["label"].split("/")[0]:
                            self.graph.remove_edge(edge[0],edge[1],key=edge[2])
        rerun = False
        nodes = copy.deepcopy(self.graph.nodes.data())
        for node in nodes:
            if node[0] != self.root:
                if not nx.has_path(self.graph,self.root,node[0]):
                    self.graph.remove_node(node[0])
                elif self.graph.out_degree(node[0]) == 0 and len(node[1]["label"]) != 1:
                    self.graph.remove_node(node[0])
                    rerun = True
        
        if rerun:
            self._fix_graph()