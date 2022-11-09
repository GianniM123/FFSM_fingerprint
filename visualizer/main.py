from sys import argv
import networkx as nx

def main():
    if len(argv) > 2:
        model = nx.drawing.nx_agraph.read_dot(argv[1])

        for node in model.nodes.data():
            node[1]["label"] = node[0] + "  " + node[1]["feature"]
        
        combine_edges = {}
        for edge in model.edges.data():
            if "label" in edge[2].keys():
                key = (edge[0],edge[1])
                if key in combine_edges:
                    combine_edges[key].append("(" + edge[2]["label"] + " " + edge[2]["feature"] + ")") 
                else:
                    combine_edges[key] = ["(" + edge[2]["label"] + " " + edge[2]["feature"] + ")"]
        
        for edge, labels in combine_edges.items():
            fin_label = ""
            for label in labels:
                fin_label = fin_label + label + "  "
                model.remove_edge(edge[0],edge[1])
            
            model.add_edge(edge[0],edge[1], label=fin_label)
        nx.drawing.nx_agraph.write_dot(model,"output/" + argv[2])
    else:
        print("Give the model and new name")
if __name__ == "__main__":
    main()