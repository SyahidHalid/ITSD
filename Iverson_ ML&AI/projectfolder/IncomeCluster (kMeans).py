from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from matplotlib import pyplot as plt

df =  pd.read_csv(".\\pandas\\income.csv")
print(df.head())

plt.scatter(df['Age'], df['Income($)'])
plt.xlabel('Age')
plt.ylabel('Income($)')

km = KMeans(n_clusters=3)
y_predicted = km.fit_predict(df[['Age','Income($)']])
df['cluster'] = y_predicted
print(km.cluster_centers_) #Centroid

df1 = df[df.cluster==0]
df2 = df[df.cluster==1]
df3 = df[df.cluster==2]
plt.scatter(df1.Age,df1['Income($)'], color='green')
plt.scatter(df2.Age,df2['Income($)'], color='Red')
plt.scatter(df3.Age,df3['Income($)'], color='black')
plt.scatter(km.cluster_centers_[:,0],
            km.cluster_centers_[:,1],
            color='purple',
            marker='*',
           label='centroid')
plt.xlabel('Age')
plt.ylabel('Income')
plt.legend()
plt.show()


#Using MinMax Scaller because of range to far
scaler = MinMaxScaler()


df[["Age","Income($)"]] = scaler.fit_transform(
    df[["Age","Income($)"]] 
)
print(df)


#scaler.fit(df[['Income($)']])
# df['Income($)'] = scaler.transform(df[['Income($)']])

# #scaler.fit(df[['Age']])
# df['Age'] = scaler.transform(df[['Age']])

plt.scatter(df.Age,df['Income($)'])

km = KMeans(n_clusters=3)
y_predicted = km.fit_predict(df[['Age','Income($)']])
df['cluster'] = y_predicted
print(km.cluster_centers_)
print(df)

# df[["Age","Income($)"]] = scaler.inverse_transform(
#     df[["Age","Income($)"]] 
# )

df1 = df[df.cluster==0]
df2 = df[df.cluster==1]
df3 = df[df.cluster==2]
plt.scatter(df1.Age,df1['Income($)'], color='green')
plt.scatter(df2.Age,df2['Income($)'], color='Red')
plt.scatter(df3.Age,df3['Income($)'], color='black')
plt.scatter(km.cluster_centers_[:,0],
            km.cluster_centers_[:,1],
            color='purple',
            marker='*',
           label='centroid')
plt.xlabel('Age')
plt.ylabel('Income')
plt.legend()
plt.show()


# df[["Age","Income($)"]] = scaler.inverse_transform(
#     df[["Age","Income($)"]] 
# )
# print(df)

# Elbow Method #sum of squared error
sse = []
k_rng = range(1,10)
for k in k_rng:
    km = KMeans(n_clusters=k)
    km.fit(df[['Age', 'Income($)']])
    sse.append(km.inertia_)

plt.xlabel('K')
plt.ylabel('Sum of squared Error')
plt.plot(k_rng, sse)
plt.show()

# ==========================================
# K-MEANS CLUSTERING
# ==========================================

# K-Means requires us to specify the number
# of clusters (K) BEFORE running the algorithm.
#
# Workflow:
# Choose K
#    ↓
# Run K-Means
#    ↓
# Assign data points to nearest centroid
#    ↓
# Get K clusters
#
# Example:
# KMeans(n_clusters=3)
#
# Question:
# "I want 3 clusters. Find them for me."

# from sklearn.cluster import KMeans
#
# km = KMeans(n_clusters=3)
# labels = km.fit_predict(X)


# PCA
# Deep Learning
# Evaluation
# Deploy
# NLP
# chat bot
