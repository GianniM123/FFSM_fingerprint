from dataclasses import dataclass
import copy
 
import networkx as nx

from base.FFSM.FFSM import FFSM, ConditionalState
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence, fresh_var, id_in_list



@dataclass
class Option:
    features: set[str]
    current_states: list[tuple[ConditionalState, set[str]]]
    graph : nx.MultiDiGraph

    def __eq__(self, other) -> bool:
        if isinstance(other, Option):
            equal = True
            for current_state_1 in self.current_states:
                match_found = False
                for current_state_2 in other.current_states:
                    if current_state_1[0] == current_state_2[0] and current_state_1[1] == current_state_2[1]: #states are equal
                        match_found = True
                        break
                equal = equal and match_found
            return (self.features == other.features and equal) 


class CADS(ConfigurationDistinguishingSequence):

    def __init__(self, ffsm : FFSM = None, ds : nx.MultiDiGraph = None ) -> None:
        super().__init__(ffsm=ffsm, ds=ds)
    
    @classmethod
    def from_file(self, file : str) -> ConfigurationDistinguishingSequence:
        ds = nx.drawing.nx_agraph.read_dot(file)
        return CADS(ds=ds)

    def _calculate_graph(self):
        self.ffsm.reset_to_initial_state()
        seen_states = []
        names = []
        root = Option(self.ffsm.features,self.ffsm.current_states, nx.MultiDiGraph())

        options : list[Option] = []
        options.append(root)

        self.graph : nx.MultiDiGraph = nx.MultiDiGraph()
        self.root = fresh_var(0)
        self.graph.add_node(self.root, label=root.features)
        names.append((root,self.root))

        root.graph.add_node(self.root,label=root.features)
        while len(options) > 0:
            to_discover = options.pop(0)
      
            to_discover_node = id_in_list(to_discover,names)
            seen_states.append(to_discover)
            for input in self.ffsm.alphabet:
                try:
                    self.ffsm.current_states = to_discover.current_states
                    outputs = self.ffsm.step(input)
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
                    new_graph = copy.deepcopy(to_discover.graph)
                    for output, features  in output_dict.items():

                        self.ffsm.current_states = to_discover.current_states
                        self.ffsm.step(input,features)
                        new_option = Option(features,self.ffsm.current_states, new_graph)

                        new_node = id_in_list(new_option,names)
                        if new_node == None:
                            new_node = fresh_var(len(names))
                            names.append((new_option,new_node))
                            new_graph.add_node(new_node, label=features)
                        elif new_node not in new_graph.nodes.keys():
                            new_graph.add_node(new_node, label=features)
                        
                        if new_node != to_discover_node and new_node != self.root:
                            new_graph.add_edge(to_discover_node, new_node, label=input + "/" + output)

                        if len(new_option.features) == 1:
                            seen_states.append(new_option)
                            self._add_model(new_option.graph)
                            filtered = list(filter(lambda x: len(x[1]["label"]) == 1, self.graph.nodes.data()))
                            just_features = set([list(x[1]["label"])[0] for x in filtered])
                            if len(just_features) == len(self.ffsm.features):
                                graph = copy.deepcopy(self.graph)
                                self._fix_graph()
                                self._remove_double_inputs()
                                filtered = list(filter(lambda x: len(x[1]["label"]) == 1, self.graph.nodes.data()))
                                just_features = set([list(x[1]["label"])[0] for x in filtered])
                                if len(just_features) == len(self.ffsm.features):
                                    options = []
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
    
    def _add_model(self, new_graph : nx.MultiDiGraph):
        for node in new_graph.nodes.data():
            if node[0] not in self.graph.nodes.keys():
                self.graph.add_node(node[0], label = node[1]["label"])
        
        for edge in new_graph.edges.data():
            has_edge = False
            for edge_graph in self.graph.out_edges(edge[0],data=True):
                if edge_graph[1] == edge[1] and edge[2]["label"] == edge_graph[2]["label"]:
                    has_edge = True
            if not has_edge:
                self.graph.add_edge(edge[0],edge[1],label=edge[2]["label"])

    def _fix_graph(self):
        # Check if the property holds that for a input Parent is subset equal to children 
        
        rerun = True
        while rerun:
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
                    if feature_set != node[1]["label"]:
                        for edge in all_edges:
                            if input == edge[3]["label"].split("/")[0]:
                                self.graph.remove_edge(edge[0],edge[1],key=edge[2])
                

        # Remove leafs that are not singular or nodes are not connected to the root

            rerun = False
            nodes = copy.deepcopy(self.graph.nodes.data())
            for node in nodes:
                if node[0] != self.root:
                    if self.graph.in_degree(node[0]) == 0 or self.graph.out_degree(node[0]) == 0 and len(node[1]["label"]) != 1:
                        self.graph.remove_node(node[0])
                        rerun = True
        
        

    def _remove_double_inputs(self):
        for node in self.graph.nodes:
            inputs = set()
            for edge in self.graph.out_edges(node, data=True):
                inputs.add(edge[2]["label"].split("/")[0])
            inputs = list(inputs)
            if len(inputs) > 1:
                edges = copy.deepcopy(self.graph.out_edges(node, data=True,keys=True))
                for edge in edges:
                    input = edge[3]["label"].split("/")[0]
                    for i in range(1,len(inputs)):
                        if input == inputs[i]:
                            self.graph.remove_edge(edge[0],edge[1],edge[2])
            
        rerun = True
        while rerun:
            rerun = False
            nodes = copy.deepcopy(self.graph.nodes.data())
            for node in nodes:
                if node[0] != self.root:
                    if self.graph.in_degree(node[0]) == 0:
                        self.graph.remove_node(node[0])
                        rerun = True
                    elif self.graph.out_degree(node[0]) == 0 and len(node[1]["label"]) != 1:
                        self.graph.remove_node(node[0])
                        rerun = True
