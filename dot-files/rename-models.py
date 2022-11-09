import os, sys
import networkx as nx

def main():
    if len(sys.argv) > 1:
        for path, _, files in os.walk(sys.argv[1]):
            for file in files:
                p = os.path.join(path,file)
                model = nx.drawing.nx_agraph.read_dot(p)
                for node in model.nodes.data():
                    if "label" in node[1].keys():
                        node[1].pop("label")
                split = p.split("/")
                if len(split) > 3:
                    version = split[1] + "-" + split[2]
                    model.graph = {}
                    model.graph["version"] = version
                    print(model.graph)
                    nx.drawing.nx_agraph.write_dot(model,sys.argv[1] + version + ".dot") #nx_agraph line 162 comment key out
     


if __name__ == "__main__":
    main()