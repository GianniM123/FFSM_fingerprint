import networkx as nx
import copy

from base.FFSM.FFSM import FFSM, RESET_IN, RESET_OUT
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence, fresh_var



class ShuLeeReset(ConfigurationDistinguishingSequence):

    def __init__(self, ffsm : FFSM = None, ds : nx.MultiDiGraph = None ) -> None:
        super().__init__(ffsm=ffsm, ds=ds)
    
    @classmethod
    def from_file(self, file : str) -> ConfigurationDistinguishingSequence:
        ds = nx.drawing.nx_agraph.read_dot(file)
        return ShuLeeReset(ds=ds)

    def _find_separating_sequence(self, config1 : str, config2 : str) -> list[str]:
        visited = []
        self.ffsm.reset_to_initial_state()
        to_explore = [(self.ffsm.current_states, self.ffsm.current_states, [])] 
        while to_explore:
            (curr1, curr2, prefix) = to_explore.pop(0)
            visited.append((curr1,curr2))
            for input in self.ffsm.alphabet:
                self.ffsm.current_states = curr1
                outputs1 = self.ffsm.step(input,{config1})
                new_curr1 = self.ffsm.current_states
                self.ffsm.current_states = curr2
                outputs2 = self.ffsm.step(input, {config2})
                new_curr2 = self.ffsm.current_states
                new_prefix = prefix + [input]
                if outputs1[0][0] != outputs2[0][0]:
                    return new_prefix
                else:
                    if (new_curr1,new_curr2) not in visited:
                        to_explore.append((new_curr1,new_curr2,new_prefix))
        raise SystemExit('Could not separate the given configurations.')

    def _calculate_graph(self):
        partition = [self.ffsm.features]
        sequences : list[list[str]] = []
        while len(partition) != len(self.ffsm.features):
            for part in partition:
                if len(part) > 1:
                    list_set = list(part)
                    config1 = list_set[0]
                    config2 = list_set[1]
                    try:
                        seq = self._find_separating_sequence(config1,config2)
                        sequences.append(seq)
                        break     
                    except Exception as e:
                        print(e)
                        raise SystemExit('Could not distinguish the given configurations.')
            new_partition = []
            self.ffsm.reset_to_initial_state()
            for config_set in partition:
                if len(config_set) == 1:
                    new_partition.append(config_set)
                else:
                    split_dict : dict[str,set] = {}
                    for config in config_set:
                        output = ""
                        self.ffsm.reset_to_initial_state()
                        for input in sequences[-1]:
                            output_list = self.ffsm.step(input,{config})
                            output = output + output_list[0][0]

                        if output in split_dict.keys():
                            split_dict[output].add(config)
                        else:
                            split_dict[output] = {config}
                    for new_part in split_dict.values():
                        new_partition.append(new_part)
            
            partition = new_partition
        self.exists = True
        self.root = fresh_var(0)
        counter = 1
        self.configuration_ss.add_node(self.root, label=self.ffsm.features)
        current_nodes = [self.root]
        for sequence in sequences:
            new_current_nodes = []
            for current_node in current_nodes:
                current_selected_node = current_node
                self.ffsm.reset_to_initial_state()
                for input in sequence:
                    output_list = self.ffsm.step(input, self.configuration_ss.nodes[current_node]["label"])
                    output_dict : dict[str, set] = {}
                    for out, features in output_list:
                        if out not in output_dict.keys():
                            output_dict[out] = set(features)
                        else:
                            output_dict[out] = output_dict[out].union(set(features))
                    new_node = None
                    for output, configurations in output_dict.items():
                        if current_selected_node in new_current_nodes:
                            new_current_nodes.remove(current_selected_node)
                        new_node = fresh_var(counter)
                        counter = counter + 1
                        self.configuration_ss.add_node(new_node, label=configurations)
                        self.configuration_ss.add_edge(current_selected_node,new_node, label=input + "/" + output)
                        new_current_nodes.append(new_node)
                    if len(output_dict.keys()) == 1:
                        current_selected_node = new_node
            current_nodes.clear()
            if sequence != sequences[-1]:
                for node in new_current_nodes:
                    new_node = fresh_var(counter)
                    counter = counter + 1
                    self.configuration_ss.add_node(new_node, label=self.configuration_ss.nodes[node]["label"])
                    self.configuration_ss.add_edge(node,new_node, label=RESET_IN + "/" + RESET_OUT)
                    current_nodes.append(new_node)



            