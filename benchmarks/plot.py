import sys

from benchmark import TIMEOUT_MIN
from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt
from bisect import bisect_left
from scipy import stats
from math import ceil

#Effect size: Vargha and Delaney’s (https://gist.github.com/jacksonpradolima/f9b19d65b7f16603c837024d5f8c8a65)
def VD_A(treatment : list, control : list):
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = stats.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
#     A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2
    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude


def calculate_effect_size(dataframe : pd.DataFrame, family_option : str, product_option :str):
    max_val = max(dataframe["number of versions"].to_list())
    new_frame = {"number of versions" : [], "effect size" : [], "magnitude" : []}
    for i in range(2,max_val+1):
        frame = dataframe[dataframe["number of versions"] == i]
        new_frame["number of versions"].append(i)

        product = frame[product_option]
        family = frame[family_option]
        estimate, magnitude = VD_A(family.to_list(), product.to_list())
        new_frame["effect size"].append(estimate)
        new_frame["magnitude"].append(magnitude)
    return pd.DataFrame.from_dict(new_frame)


def plot_shulee(file : str, option : str):
    fam = "family " + option
    prod = "product " + option
    dataframe = pd.read_csv(file)
    dataframe = dataframe[[fam, prod, "number of versions"]]
    grouped_frame = dataframe.groupby('number of versions')
    mean_frame = grouped_frame.mean()
    mean_frame.rename(columns={fam: "Avg. family", prod: "Avg. product"}, inplace=True)
    std_frame = grouped_frame.std()
    std_frame.rename(columns={fam: "Std. family", prod: "Std. product"}, inplace=True)
    mean_std_frame = pd.concat([mean_frame,std_frame],axis=1)
    mean_std_frame = mean_std_frame.reindex(columns=["Avg. family","Std. family", "Avg. product", "Std. product"])
    display(mean_std_frame)
    effect_size = calculate_effect_size(dataframe,prod, fam)
    display(effect_size)

    fig, axs = plt.subplots(2)
    max_val = ceil(max(dataframe[fam].to_list()) * 100)/100
    dataframe.boxplot(by='number of versions',ax=axs)
    fig.set_size_inches(10,12)
    axs[0].set_title("Family-based " + option)
    axs[1].set_title("Product-based " + option)
    for ax in axs:
        ax.set_ylim((0,max_val))
        ax.set_ylabel("Calculation time (s)")
        ax.set_xlabel("Number of versions")
    fig.suptitle("")
    plt.savefig('oms-plot-' + option + '.pdf')

def plot_cds(file : str):
    dataframe = pd.read_csv(file)
    ADS_frame = dataframe[["number of versions", "cADS time", "cADS nodes size", "cADS edges size", "cADS reset", "cADS depth"]]
    ADS_frame = ADS_frame[ADS_frame["cADS time"] != TIMEOUT_MIN]

    PDS_frame = dataframe[["number of versions", "cPDS time", "cPDS nodes size", "cPDS edges size", "cPDS reset", "cPDS depth"]]
    PDS_frame = PDS_frame[PDS_frame["cPDS time"] != TIMEOUT_MIN]
    display(PDS_frame)

    total_mean_frame = pd.DataFrame()
    total_std_frame = pd.DataFrame()
    total_min_frame = pd.DataFrame()
    total_max_frame = pd.DataFrame()

    for frame in [PDS_frame, ADS_frame]:
        grouped_frame = frame.groupby('number of versions')
        mean_frame = grouped_frame.mean()
        mean_frame = mean_frame.add_suffix("_mean")
        total_mean_frame = pd.concat([mean_frame, total_mean_frame],axis=1)

        std_frame = grouped_frame.std()
        std_frame = std_frame.add_suffix("_std")
        total_std_frame = pd.concat([std_frame, total_std_frame],axis=1)

        min_frame = grouped_frame.min()
        min_frame = min_frame.add_suffix("_min")
        total_min_frame = pd.concat([min_frame, total_min_frame],axis=1)

        max_frame = grouped_frame.max()
        max_frame = max_frame.add_suffix("_max")
        total_max_frame = pd.concat([max_frame, total_max_frame],axis=1)

    big_frame = pd.concat([total_mean_frame, total_std_frame, total_min_frame, total_max_frame],axis=1)

    time_frame = pd.DataFrame()
    nodes_frame = pd.DataFrame()
    edges_frame = pd.DataFrame()
    reset_frame = pd.DataFrame()
    depth_frame = pd.DataFrame()

    for suffix in ["_mean", "_std", "_min", "_max"]:
        for column in ["cADS time", "cPDS time"]:
            time_frame.insert(0,column + suffix,big_frame[column+suffix])
        for column in ["cADS nodes size", "cPDS nodes size"]:
            nodes_frame.insert(0,column + suffix,big_frame[column+suffix])
        for column in ["cADS edges size", "cPDS edges size"]:
            edges_frame.insert(0,column + suffix,big_frame[column+suffix])
        for column in ["cADS reset", "cPDS reset"]:
            reset_frame.insert(0,column + suffix,big_frame[column+suffix])
        for column in ["cADS depth", "cPDS depth"]:
            depth_frame.insert(0,column + suffix,big_frame[column+suffix])
    
    
    display(time_frame)
    display(nodes_frame)
    display(edges_frame)
    display(reset_frame)
    display(depth_frame)

    fig, axs = plt.subplots(1,2)
    max_val = ceil(max(dataframe[["number of versions", "cADS time", "cPDS time"]].replace(1200,0)["cPDS time"].to_list()))*1.05
    fig.set_size_inches(10,12)
    ADS_frame[["number of versions", "cADS time"]].boxplot(by="number of versions",ax=axs[0])
    PDS_frame[["number of versions", "cPDS time"]].boxplot(by="number of versions",ax=axs[1])

    axs[0].set_title("cADS execution time")
    axs[1].set_title("cPDS execution time")
    for ax in axs:
        ax.set_ylim((0,max_val))
        ax.set_ylabel("Calculation time (s)")
        ax.set_xlabel("Number of versions")

    effect_size = calculate_effect_size(dataframe, "cPDS time", "cADS time")
    display(effect_size)
    # for column in ["number of versions", "cADS time", "cADS nodes size", "cADS edges size", "cADS reset",  "cADS depth", "cPDS time", "cPDS nodes size",  "cPDS edges size", "cPDS reset",  "cPDS depth"]:
    #     pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = sys.argv[1]
        index = file.find("cds")
        if index == -1:
            plot_shulee(file, "asc")
            plot_shulee(file,"desc")
        else:
            plot_cds(file)
        plt.show()
      