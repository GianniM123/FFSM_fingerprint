import subprocess
import re
from time import sleep
import pandas as pd
import shlex
import sys
import networkx as nx

FAMILY = "python3 ../family-based_fingerprinter/main.py --FFSM={ffsm} --active={fsm} --{option}"

PRODUCTS = "python3 ../product-based_fingerprinter/main.py --folder={folder} --sut={fsm}"



FFSM = "../dot-files/{version}/combined/{type}/{version}-distinct_{number}.dot"
FSM = "../dot-files/{version}/0.9.7-TLS10.dot"
FOLDER = "../dot-files/{version}/distinct/{type}/{number}"

TIMEOUT_MIN = 20 * 60

def get_time(process : subprocess.Popen):
    try:
        process.wait(timeout=TIMEOUT_MIN)
        result = process.stdout.read()
        process.terminate()
        time = float(re.search("[0-9]+.[0-9]+\s",str(result)).group())
        return time
    except:
        process.terminate()
        return TIMEOUT_MIN

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

def extract_info_from_graph(file : str):
    graph : nx.MultiDiGraph = nx.drawing.nx_agraph.read_dot(file)
    return_dict = {"mean input" : 0,  "mean reset" : 0, "depth" : 0, "max reset" : 0}
    for node in graph.nodes.data():
        if graph.out_degree(node[0]) == 0:
            path = nx.shortest_path(graph,"a0", node[0])
            depth = len(path) - 1
            return_dict["mean input"] = return_dict["mean input"] + depth
            if return_dict["depth"] < depth:
                return_dict["depth"] = depth
            nr_of_resets = 0
            for node in path:
                if graph.nodes[node]["label"] == "RESET-SYS":
                    nr_of_resets = nr_of_resets + 1
                    return_dict["mean reset"] = return_dict["mean reset"] + 1
            if return_dict["max reset"] < nr_of_resets:
                    return_dict["max reset"] = nr_of_resets
            
    return return_dict

def run_cds_benchmark(option : str):
    time_dict = {"number of versions" : [], "cADS time" : [], "cADS mean input" : [],"cADS mean reset" : [],  "cADS depth" : [], "cADS max reset" : [],"cPDS time" : [], "cPDS mean input" : [], "cPDS mean reset" : [],  "cPDS depth" : [],"cPDS max reset" : [], }
    for i in range(2,17):
        print("at nr: ", i)
        for _ in range(0,10):
            time_dict["number of versions"].append(i)
            ffsm = FFSM.format(version=option, type="asc", number=i)
            fsm = FSM.format(version=option)

            time_ads = run_family_fingerprinter(ffsm,fsm,"adaptive")
            if time_ads != TIMEOUT_MIN:
                info_dict = extract_info_from_graph('CDS.dot')
                time_dict["cADS time"].append(time_ads)
                time_dict["cADS mean input"].append(info_dict["mean input"]/i)
                time_dict["cADS mean reset"].append(info_dict["mean reset"]/i)
                time_dict["cADS max reset"].append(info_dict["max reset"])
                time_dict["cADS depth"].append(info_dict["depth"])
            else:
                time_dict["cADS time"].append(TIMEOUT_MIN)
                time_dict["cADS mean input"].append(0)
                time_dict["cADS mean reset"].append(0)
                time_dict["cADS max reset"].append(0)
                time_dict["cADS depth"].append(0)

            time_pds = run_family_fingerprinter(ffsm,fsm,"preset")
            if time_pds != TIMEOUT_MIN:
                info_dict = extract_info_from_graph('CDS.dot')
                time_dict["cPDS time"].append(time_pds)
                time_dict["cPDS mean input"].append(info_dict["mean input"]/i)
                time_dict["cPDS mean reset"].append(info_dict["mean reset"]/i)
                time_dict["cPDS max reset"].append(info_dict["max reset"])
                time_dict["cPDS depth"].append(info_dict["depth"])
            else:
                time_dict["cPDS time"].append(TIMEOUT_MIN)
                time_dict["cPDS mean input"].append(0)
                time_dict["cPDS mean reset"].append(0)
                time_dict["cPDS max reset"].append(0)
                time_dict["cPDS depth"].append(0)

    df = pd.DataFrame.from_dict(time_dict) 
    df.to_csv ('benchmark_cds_' + option  + '.csv', index = False, header=True)

def run_family_benchmark(option : str):
    time_dict = {"number of versions" : [], "cADS time" : [], "cADS mean input" : [],"cADS mean reset" : [],  "cADS depth" : [], "cADS max reset" : [], "OMS time" : [],  "OMS mean input" : [], "OMS mean reset" : [],  "OMS depth" : [], "OMS max reset" : [], }
    for i in range(2,17):
        print("at nr: ", i)
        for _ in range(0,50):
            time_dict["number of versions"].append(i)
            ffsm = FFSM.format(version=option, type="asc", number=i)
            fsm = FSM.format(version=option)

            time_ads = run_family_fingerprinter(ffsm,fsm,"adaptive")
            if time_ads != TIMEOUT_MIN:
                info_dict = extract_info_from_graph('CDS.dot')
                time_dict["cADS time"].append(time_ads)
                time_dict["cADS mean input"].append(info_dict["mean input"]/i)
                time_dict["cADS mean reset"].append(info_dict["mean reset"]/i)
                time_dict["cADS max reset"].append(info_dict["max reset"])
                time_dict["cADS depth"].append(info_dict["depth"])
            else:
                time_dict["cADS time"].append(TIMEOUT_MIN)
                time_dict["cADS nodes size"].append(0)
                time_dict["cADS mean input"].append(0)
                time_dict["cADS mean reset"].append(0)
                time_dict["cADS max reset"].append(0)
                time_dict["cADS depth"].append(0)

            time_oms = run_family_fingerprinter(ffsm,fsm,"shulee")
            info_dict = extract_info_from_graph('CDS.dot')
            time_dict["OMS time"].append(time_oms)
            time_dict["OMS mean input"].append(info_dict["mean input"]/i)
            time_dict["OMS mean reset"].append(info_dict["mean reset"]/i)
            time_dict["OMS max reset"].append(info_dict["max reset"])
            time_dict["OMS depth"].append(info_dict["depth"])

    df = pd.DataFrame.from_dict(time_dict) 
    df.to_csv ('benchmark_family_' + option  + '.csv', index = False, header=True)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "shulee":
            run_shulee_benchmark("openssl")
        elif sys.argv[1] == "cds":
            run_cds_benchmark("openssl")
        elif sys.argv[1] == "family":
            run_family_benchmark("openssl")
        elif sys.argv[1] == "all":
            run_shulee_benchmark("openssl")
            run_cds_benchmark("openssl")
            run_family_benchmark("openssl")
     
