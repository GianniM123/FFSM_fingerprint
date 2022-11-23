import subprocess
import re
import pandas as pd
import shlex

FAMILY = "python3 ../family-fingerprinter/main.py --FFSM=../dot-files/openssl/combined/openssl-distinct_{number}.dot --active=../dot-files/openssl/0.9.7-TLS10.dot --{option}"

PRODUCTS = "python3 ../product-fingerprinter/main.py --folder ../dot-files/openssl/distinct/{number} --sut=../dot-files/openssl/0.9.7-TLS10.dot"





if __name__ == "__main__":
    time_dict = {"number of versions" : [], "family" : [], "product" : []}
    for i in range(6,17):
        print("at nr: ", i)
        for j in range(0,100):
            time_dict["number of versions"].append(i)

            process = subprocess.Popen(shlex.split(FAMILY.format(number=i, option="shulee")),stdout=subprocess.PIPE)
            process.wait()
            result = process.stdout.read()
            process.terminate()
            time_family = float(re.search("[0-9].[0-9]+\s",str(result)).group())
            time_dict["family"].append(time_family)

            process = subprocess.Popen(shlex.split(PRODUCTS.format(number=i)), stdout=subprocess.PIPE)
            process.wait()
            result = process.stdout.read()
            process.terminate()
            time_product = float(re.search("[0-9].[0-9]+\s",str(result)).group())
            time_dict["product"].append(time_product)

    df = pd.DataFrame.from_dict(time_dict) 
    df.to_csv (r'benchmark_shu_lee.csv', index = False, header=True)
