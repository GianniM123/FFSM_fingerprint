from time import sleep
from aalpy.SULs.AutomataSUL import MealySUL
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence
from base.FFSM.FFSM import RESET_IN, RESET_OUT



class Simulator:
    
    def __init__(self, ds : ConfigurationDistinguishingSequence) -> None:
        self.ds = ds

      
    def _ds_fingerprint(self, sul : MealySUL) -> str:
        self.total_queries = []
        if self.ds.exists == True:
            current_node = self.ds.root
            while self.ds.seperating_sequence.out_degree(current_node) > 0:
                input = self.ds.seperating_sequence.nodes[current_node]["label"]
                output = None
                if input == RESET_IN:
                    sul.pre()
                    sleep(0.2)
                    output = RESET_OUT
                else:
                    output = sul.step(input)
                self.total_queries.append((input,output))
            	
                found = False
                for edge in self.ds.seperating_sequence.out_edges(current_node, data=True):
                    if edge[2]["label"] == str(output):
                        current_node = edge[1]
                        found = True
                        break
                if not found:
                    return ""

            return self.ds.seperating_sequence.nodes[current_node]["label"]
        else:
            return ""


    def fingerprint_system(self, sul : MealySUL) -> str:
        config = self._ds_fingerprint(sul)
        print("nr of inputs: ", len(self.total_queries))
        only_reset = list(filter(lambda x : x[0] == RESET_IN, self.total_queries))
        print("nr of resets: ", len(only_reset))
        return config


