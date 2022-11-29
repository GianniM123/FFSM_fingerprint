import sys

from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt


def plot(option : str):
      dataframe = pd.read_csv(sys.argv[1])
      dataframe = dataframe[["family " + option, "product " + option, "number of versions"]]
      grouped_frame = dataframe.groupby('number of versions')
      mean_frame = grouped_frame.mean()
      mean_frame.rename(columns={"family " + option: "Avg. family", "product " + option: "Avg. product"}, inplace=True)
      std_frame = grouped_frame.std()
      std_frame.rename(columns={"family " + option: "Std. family", "product " + option: "Std. product"}, inplace=True)
      mean_std_frame = pd.concat([mean_frame,std_frame],axis=1)
      print(mean_std_frame)
      mean_std_frame = mean_std_frame.reindex(columns=["Avg. family","Std. family", "Avg. product", "Std. product"])
      display(mean_std_frame)
      mean_frame.plot()
      fig, axs = plt.subplots(2)

      dataframe.boxplot(by='number of versions',ax=axs)
      for ax in axs:
         ax.set_ylim((0,0.10))
         ax.set_ylabel("Calculation time (s)")
         ax.set_xlabel("Number of versions")
      fig.suptitle("")
      


if __name__ == "__main__":
   if len(sys.argv) > 1:
      plot("asc")
      plot("desc")
      plt.show()
      