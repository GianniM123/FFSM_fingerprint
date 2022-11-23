import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    dataframe = pd.read_csv(r'benchmark_shu_lee.csv')
    mean_frame = dataframe.groupby('number of versions').mean()
    print(mean_frame)
    mean_frame.plot()
    dataframe.boxplot(by='number of versions')
    plt.show()
    