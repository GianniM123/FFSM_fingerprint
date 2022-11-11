from abc import ABC, abstractmethod
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

    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm : FFSM = ffsm
        self.exists : bool = False
        self.configuration_ss : nx.MultiDiGraph = None
        self.root = None
        self._calculate_graph()
        print(self.exists)
        if self.exists:
            self._parse_distinguishing_sequence()
            nx.drawing.nx_agraph.write_dot(self.seperating_sequence,"CDS.dot")

    @abstractmethod
    def _calculate_graph(self) -> None:
        pass

    def _parse_distinguishing_sequence(self) -> None:
        self.seperating_sequence = copy.deepcopy(self.configuration_ss)
        for node in self.seperating_sequence.nodes(data = True):
            if self.seperating_sequence.out_degree(node[0]) > 0:
              for edge in self.seperating_sequence.out_edges(node[0], data=True):
                input, output = edge[2]["label"].split("/")
                node[1]["label"] = input
                edge[2]["label"] = output  


