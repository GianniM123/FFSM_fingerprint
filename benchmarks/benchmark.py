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


if __name__ == "__main__":
    time_dict = {"number of versions" : [], "family" : [], "product" : []}
    if len(sys.argv) > 1:
        if sys.argv[1] == "openssl" or sys.argv[1] == "mbedtls":
            max_itr = 17 if sys.argv[1] == "openssl" else 7
            for i in range(2,max_itr):
                ffsm = FFSM.format(version=sys.argv[1], number=i)
                fsm = FSM.format(version=sys.argv[1])
                folder = FOLDER.format(version=sys.argv[1], number=i)
                print("at nr: ", i)
                for j in range(0,100):
                    time_dict["number of versions"].append(i)

                    process = subprocess.Popen(shlex.split(FAMILY.format(ffsm=ffsm, fsm=fsm,option="shulee")),stdout=subprocess.PIPE)
                    process.wait()
                    result = process.stdout.read()
                    process.terminate()
                    time_family = float(re.search("[0-9].[0-9]+\s",str(result)).group())
                    time_dict["family"].append(time_family)

                    process = subprocess.Popen(shlex.split(PRODUCTS.format(folder=folder, fsm=fsm)), stdout=subprocess.PIPE)
                    process.wait()
                    result = process.stdout.read()
                    process.terminate()
                    time_product = float(re.search("[0-9].[0-9]+\s",str(result)).group())
                    time_dict["product"].append(time_product)

        df = pd.DataFrame.from_dict(time_dict) 
        df.to_csv ('benchmark_shu_lee_' + sys.argv[1] + '.csv', index = False, header=True)
