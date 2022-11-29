from abc import ABC, abstractmethod, abstractclassmethod
import copy
from base.FFSM.FFSM import FFSM

import networkx as nx



def fresh_var(index : int):
    '''Generate a fresh variable on basis of the given index'''
    return "a" + str(index)

def id_in_list(id, list):
    for ids in list:
        if ids[0] == id:
            return ids[1]
    return None

class ConfigurationDistinguishingSequence(ABC):

    def __init__(self, ffsm : FFSM = None, ds : nx.MultiDiGraph = None) -> None:
        if ffsm is None and ds is None:
            SystemExit("Give either a FFSM or a distinguishing sequence")
        elif ffsm is not None:
            self.ffsm : FFSM = ffsm
            self.exists : bool = False
            self.configuration_ss : nx.MultiDiGraph = nx.MultiDiGraph()
            self.root = None
            self._calculate_graph()
            if self.exists:
                self._parse_distinguishing_sequence()
                
        else:
            self.seperating_sequence = ds
            self.exists = True
            for node in self.seperating_sequence.nodes:
                if self.seperating_sequence.in_degree(node) == 0:
                    self.root = node
                    break
            

    @abstractmethod
    def _calculate_graph(self) -> None:
        pass

    @abstractclassmethod
    def from_file(self, file : str) -> 'ConfigurationDistinguishingSequence':
        pass

    def _parse_distinguishing_sequence(self) -> None:
        self.seperating_sequence = copy.deepcopy(self.configuration_ss)
        for node in self.seperating_sequence.nodes(data = True):
            if self.seperating_sequence.out_degree(node[0]) > 0:
              for edge in self.seperating_sequence.out_edges(node[0], data=True):
                input, output = edge[2]["label"].split("/")
                node[1]["label"] = input
                edge[2]["label"] = output  


