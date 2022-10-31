from copy import deepcopy

from aalpy.SULs.AutomataSUL import MealySUL
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence


class Simulator:
    
    def __init__(self, ds : ConfigurationDistinguishingSequence) -> None:
        self.ds = ds

      
    def _pds_fingerprint(self, sul : MealySUL) -> set[str]:
        self.total_queries = []
        if self.ds.exists == True:
            current_node = self.ds.root
            while self.ds.seperating_sequence.out_degree(current_node) > 0:
                input = self.ds.seperating_sequence.nodes[current_node]["label"]
                output = sul.step(input)
                self.total_queries.append((input,output))

                for edge in self.ds.seperating_sequence.out_edges(current_node, data=True):
                    if edge[2]["label"] == output:
                        current_node = edge[1]

            return self.ds.seperating_sequence.nodes[current_node]["label"]
        else:
            return set()


    def fingerprint_system(self, sul : MealySUL) -> set[str]:
        # features = self._do_random_input(self.hdt.root,sul)
        features = self._pds_fingerprint(sul)
        print(self.total_queries)
        return features


