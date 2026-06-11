# supervised learning
# Linear
# logistic
# Decision Tree 
# Random Forest 

# unsupervised learning

# Reinforcement learning

# Deep Learning

#tensorflow
#pytorch


#data preparation
#x is label endcoder in ML that change into number
#scaling from 10000 become 0 - 1



import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

df = pd.read_csv(".\\pandas\\homeprices.csv")

# Visualise
plt.figure(figsize=(10, 6))
plt.scatter(df['area'],df['price'],
            color='red',
            marker="+")
plt.xlabel('Area')
plt.ylabel('Price')
plt.show

# Prepare
X = df.drop('price', axis='columns')
y = df['price']

print("features:\n",X)
print("target:\n",y)

# Train Linear REgression
model = linear_model.LinearRegression()
model.fit(X,y)

#Predictions
model.predict([[3300]])

#y = mx+c
print("Gradient(m): ", model.coef_)
print("Intercept(c): ", model.intercept_)

#Manual calculation
price = 3300*model.coef_[0] + model.intercept_

#prediction
area = pd.read_csv(".\\pandas\\areas.csv")

p = model.predict(area)
area['prices'] = p

#save predictions
area.to_csv(".\\pandas\\areaprediction (Created).csv", index=False)

# Visualise
plt.figure(figsize=(10, 6))
plt.scatter(df['area'],df['price'],
            color='red',
            marker="+")

plt.plot(df['area'],model.predict(df[['area']]),
         color='blue')
plt.xlabel('Area')
plt.ylabel('Price')
plt.show