import subprocess
import re
import pandas as pd
import shlex
import sys

FAMILY = "python3 ../family-fingerprinter/main.py --FFSM={ffsm} --active={fsm} --{option}"

PRODUCTS = "python3 ../product-fingerprinter/main.py --folder={folder} --sut={fsm}"



FFSM = "../dot-files/{version}/combined/{type}/{version}-distinct_{number}.dot"
FSM = "../dot-files/{version}/1.0.0-TLS10.dot"
FOLDER = "../dot-files/{version}/distinct/{type}/{number}"


def get_time(process : subprocess.Popen):
    process.wait()
    result = process.stdout.read()
    process.terminate()
    time = float(re.search("[0-9].[0-9]+\s",str(result)).group())
    return time

def run_family_fingerprinter(ffsm,fsm,option) -> float:
    process = subprocess.Popen(shlex.split(FAMILY.format(ffsm=ffsm, fsm=fsm,option=option)),stdout=subprocess.PIPE)
    return get_time(process)

def run_product_fingerprinter(folder,fsm) -> float:
    process = subprocess.Popen(shlex.split(PRODUCTS.format(folder=folder, fsm=fsm)), stdout=subprocess.PIPE)
    return get_time(process)


def run_benchmark(option : str):
    time_dict = {"number of versions" : [], "family asc" : [], "product asc" : [], "family desc" : [], "product desc" : []}
    for i in range(2,17):
            print("at nr: ", i)
            for j in range(0,100):
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if (sys.argv[1] == "openssl" or sys.argv[1] == "mbedtls"):
            run_benchmark(sys.argv[1])
        elif(sys.argv[1] == "all"):
            run_benchmark("openssl")
            run_benchmark("mbedtls")
     
