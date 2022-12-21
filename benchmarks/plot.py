import sys

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


def calculate_effect_size(dataframe : pd.DataFrame, option : str):
    max_val = max(dataframe["number of versions"].to_list())
    new_frame = {"number of versions" : [], "effect size" : [], "magnitude" : []}
    for i in range(2,max_val+1):
        frame = dataframe[dataframe["number of versions"] == i]
        new_frame["number of versions"].append(i)

        product = frame["product " + option]
        family = frame["family " + option]
        estimate, magnitude = VD_A(family.to_list(), product.to_list())
        new_frame["effect size"].append(estimate)
        new_frame["magnitude"].append(magnitude)
    return pd.DataFrame.from_dict(new_frame)


def plot(option : str):
    dataframe = pd.read_csv(sys.argv[1])
    dataframe = dataframe[["family " + option, "product " + option, "number of versions"]]
    grouped_frame = dataframe.groupby('number of versions')
    mean_frame = grouped_frame.mean()
    mean_frame.rename(columns={"family " + option: "Avg. family", "product " + option: "Avg. product"}, inplace=True)
    std_frame = grouped_frame.std()
    std_frame.rename(columns={"family " + option: "Std. family", "product " + option: "Std. product"}, inplace=True)
    mean_std_frame = pd.concat([mean_frame,std_frame],axis=1)
    mean_std_frame = mean_std_frame.reindex(columns=["Avg. family","Std. family", "Avg. product", "Std. product"])
    display(mean_std_frame)
    effect_size = calculate_effect_size(dataframe, option)
    display(effect_size)

    fig, axs = plt.subplots(2)
    max_val = ceil(max(dataframe["family " + option].to_list()) * 100)/100
    dataframe.boxplot(by='number of versions',ax=axs)
    fig.set_size_inches(10,12)
    axs[0].set_title("Family-based " + option)
    axs[1].set_title("Product-based " + option)
    for ax in axs:
        ax.set_ylim((0,max_val))
        ax.set_ylabel("Calculation time (s)")
        ax.set_xlabel("Number of versions")
    fig.suptitle("")
      


if __name__ == "__main__":
   if len(sys.argv) > 1:
      plot("asc")
      plt.savefig('plot-asc.pdf')
      plot("desc")
      plt.savefig('plot-desc.pdf')
      plt.show()
      