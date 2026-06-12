# kMean Clustering

import pandas as pd
import numpy as np

df = pd.read_csv(".\\pandas\\income.csv")

df.info()
df.shape

df[df.columns[6]].value_counts()

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

plt.scatter(df['Age', df['Income($)']])




