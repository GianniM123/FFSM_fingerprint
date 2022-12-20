import subprocess
import re
from time import sleep
import pandas as pd
import shlex
import sys
import networkx as nx

FAMILY = "python3 ../family-fingerprinter/main.py --FFSM={ffsm} --active={fsm} --{option}"

PRODUCTS = "python3 ../product-fingerprinter/main.py --folder={folder} --sut={fsm}"



FFSM = "../dot-files/{version}/combined/{type}/{version}-distinct_{number}.dot"
FSM = "../dot-files/{version}/0.9.7-TLS10.dot"
FOLDER = "../dot-files/{version}/distinct/{type}/{number}"

TIMEOUT_MIN = 5 * 60

def get_time(process : subprocess.Popen):
    try:
        process.wait(timeout=TIMEOUT_MIN)
        result = process.stdout.read()
        process.terminate()
        time = float(re.search("[0-9].[0-9]+\s",str(result)).group())
        return time
    except:
        return TIMEOUT_MIN + 1

def run_family_fingerprinter(ffsm,fsm,option) -> float:
    process = subprocess.Popen(shlex.split(FAMILY.format(ffsm=ffsm, fsm=fsm,option=option)),stdout=subprocess.PIPE)
    return get_time(process)

def run_product_fingerprinter(folder,fsm) -> float:
    process = subprocess.Popen(shlex.split(PRODUCTS.format(folder=folder, fsm=fsm)), stdout=subprocess.PIPE)
    return get_time(process)


def run_shulee_benchmark(option : str):
    time_dict = {"number of versions" : [], "family asc" : [], "product asc" : [], "family desc" : [], "product desc" : []}
    for i in range(2,17):
            print("at nr: ", i)
            for _ in range(0,100):
                time_dict["number of versions"].append(i)
                for sort in ["asc", "desc"]:
                    ffsm = FFSM.format(version=option, type=sort, number=i)
                    fsm = FSM.format(version=option)
                    folder = FOLDER.format(version=option,type=sort, number=i)
                    time1 = run_family_fingerprinter(ffsm,fsm,"shulee")
                    time2 = run_product_fingerprinter(folder,fsm)

                    time_dict["family " + sort].append(time1)
                    time_dict["product " + sort].append(time2)
    df = pd.DataFrame.from_dict(time_dict) 
    df.to_csv ('benchmark_shulee_' + option  + '.csv', index = False, header=True)

def extract_info_from_graph():
    graph : nx.MultiDiGraph = nx.drawing.nx_agraph.read_dot('CDS.dot')
    return_dict = {"size" : len(graph.nodes), "reset" : 0, "depth" : 0}
    for node in graph.nodes.data():
        if node[1]["label"] == "RESET-SYS":
            return_dict["reset"] = return_dict["reset"] + 1
        elif graph.out_degree(node[0]) == 0:
            distance = nx.shortest_path_length(graph,"a0", node[0])
            if return_dict["depth"] < distance:
                return_dict["depth"] = distance
    return return_dict

def run_cds_benchmark(option : str):
    time_dict = {"number of versions" : [], "cADS time" : [], "cADS size" : [], "cADS reset" : [],  "cADS depth" : [], "cPDS time" : [], "cPDS size" : [], "cPDS reset" : [],  "cPDS depth" : [], }
    for i in range(2,16):
        print("at nr: ", i)
        max_j = 10 if i <= 8 else 4
        for _ in range(0,max_j):
            time_dict["number of versions"].append(i)
            ffsm = FFSM.format(version=option, type="asc", number=i)
            fsm = FSM.format(version=option)

            time_ads = run_family_fingerprinter(ffsm,fsm,"adaptive")
            if time_ads != TIMEOUT_MIN:
                info_dict = extract_info_from_graph()
                time_dict["cADS time"].append(time_ads)
                time_dict["cADS size"].append(info_dict["size"])
                time_dict["cADS reset"].append(info_dict["reset"])
                time_dict["cADS depth"].append(info_dict["depth"])
            else:
                time_dict["cADS time"].append(TIMEOUT_MIN)
                time_dict["cADS size"].append(0)
                time_dict["cADS reset"].append(0)
                time_dict["cADS depth"].append(0)

            time_pds = run_family_fingerprinter(ffsm,fsm,"preset")
            if time_pds != TIMEOUT_MIN:
                info_dict = extract_info_from_graph()
                time_dict["cPDS time"].append(time_pds)
                time_dict["cPDS size"].append(info_dict["size"])
                time_dict["cPDS reset"].append(info_dict["reset"])
                time_dict["cPDS depth"].append(info_dict["depth"])
            else:
                time_dict["cPDS time"].append(TIMEOUT_MIN)
                time_dict["cPDS size"].append(0)
                time_dict["cPDS reset"].append(0)
                time_dict["cPDS depth"].append(0)

    df = pd.DataFrame.from_dict(time_dict) 
    df.to_csv ('benchmark_cds_' + option  + '.csv', index = False, header=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "shulee":
            run_shulee_benchmark("openssl")
        elif sys.argv[1] == "cds":
            run_cds_benchmark("openssl")
        elif sys.argv[1] == "all":
            run_shulee_benchmark("openssl")
            run_cds_benchmark("openssl")
     
