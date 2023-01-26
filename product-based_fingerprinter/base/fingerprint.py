import networkx as nx
from aalpy.SULs.AutomataSUL import MealySUL
from aalpy.automata import MealyMachine
from base.SeparatingSequence import RESET_IN, RESET_OUT

def fingerprint_system(sut : MealySUL, distinguishing_graph : nx.MultiDiGraph) -> MealyMachine:
    total_queries = []

    current_node = None
    for node in distinguishing_graph.nodes():
        if distinguishing_graph.in_degree(node) == 0:
            current_node = node
            break

    while distinguishing_graph.out_degree(current_node) > 0:
        input = distinguishing_graph.nodes[current_node]["label"]
        output = None
        if input == RESET_IN:
            sut.pre()
            output = RESET_OUT
        else:
            output = sut.step(input)
        total_queries.append((input,output))
        
        found = False
        for edge in distinguishing_graph.out_edges(current_node, data=True):
            if edge[2]["label"] == str(output):
                current_node = edge[1]
                found = True
                break
        if not found:
            return set()
    print("nr of inputs: ", len(total_queries))
    only_reset = list(filter(lambda x : x[0] == RESET_IN, total_queries))
    print("nr of resets: ", len(only_reset))
    
    return distinguishing_graph.nodes[current_node]["label"]

