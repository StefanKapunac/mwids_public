import pandas as pd
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp
from matplotlib import pyplot as plt

def statistical_test(df: pd.DataFrame):
    columns = [df.iloc[:,i] for i in range(df.shape[1])]
    print(friedmanchisquare(*columns))
    nemenyi_res = sp.posthoc_nemenyi_friedman(df)
    print(nemenyi_res)
    ranks = df.rank(axis=1)
    avg_ranks = ranks.mean()
    print(avg_ranks)
    sp.critical_difference_diagram(avg_ranks, nemenyi_res)
    plt.show()

def main():
    df1 = pd.read_csv('../stats_data/random.csv')
    df2 = pd.read_csv('../stats_data/random_geometric.csv')
    df = pd.concat([df1, df2])
    df = df.iloc[:,3:8]
    print(df)
    statistical_test(df)

if __name__ == "__main__":
    main()