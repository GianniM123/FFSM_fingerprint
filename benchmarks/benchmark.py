import subprocess
import re
import pandas as pd
import shlex
import sys

FAMILY = "python3 ../family-fingerprinter/main.py --FFSM={ffsm} --active={fsm} --{option}"

PRODUCTS = "python3 ../product-fingerprinter/main.py --folder={folder} --sut={fsm}"



FFSM = "../dot-files/{version}/combined/{version}-distinct_{number}.dot"
FSM = "../dot-files/{version}/1.0.0-TLS10.dot"
FOLDER = "../dot-files/{version}/distinct/{number}"


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


if __name__ == "__main__":
    if len(sys.argv) > 2:
        if (sys.argv[2] == "openssl" or sys.argv[2] == "mbedtls") and (sys.argv[1] == "family" or sys.argv[1] == "shulee"):
            index1 = "family" if sys.argv[1] == "shulee" else "adaptive"
            index2 = "product" if sys.argv[1] == "shulee" else "preset"
            time_dict = {"number of versions" : [], index1 : [], index2 : []}
            max_itr = 17 if sys.argv[2] == "openssl" else 7
            if sys.argv[1] != "shulee" and sys.argv[2] == "openssl":
                max_itr = 8
            for i in range(2,max_itr):
                ffsm = FFSM.format(version=sys.argv[2], number=i)
                fsm = FSM.format(version=sys.argv[2])
                folder = FOLDER.format(version=sys.argv[2], number=i)
                print("at nr: ", i)
                for j in range(0,20):
                    time_dict["number of versions"].append(i)

                    time1 = time2 = None
                    if sys.argv[1] == "shulee":
                        time1 = run_family_fingerprinter(ffsm,fsm,"shulee")
                        time2 = run_product_fingerprinter(folder,fsm)
                    else:
                        time1 = run_family_fingerprinter(ffsm,fsm,index1)
                        time2 = run_family_fingerprinter(ffsm,fsm,index2)

                    time_dict[index1].append(time1)
                    time_dict[index2].append(time2)

        df = pd.DataFrame.from_dict(time_dict) 
        df.to_csv ('benchmark_' + sys.argv[1] + "_" + sys.argv[2] + '.csv', index = False, header=True)
