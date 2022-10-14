from sys import argv
import networkx as nx

def main():
    if len(argv) > 2:
        model = nx.drawing.nx_agraph.read_dot(argv[1])
        for node in model.nodes.data():
            node[1]["label"] = node[0] + " " + node[1]["feature"]
        
        for edge in model.edges.data():
            if "label" in edge[2].keys():
                edge[2]["label"] = edge[2]["label"] + " " + edge[2]["feature"]
        nx.drawing.nx_agraph.write_dot(model,"output/" + argv[2])
    else:
        print("Give the model and new name")
if __name__ == "__main__":
    main()