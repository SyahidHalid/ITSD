import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

df = pd.read_csv(".\\pandas\\homepricesMulti.csv")

df.info()

#1. handle missing values
#2. create a feature and target
#3. train multivariate linear regression
#4. do predictions
#5. model parameter (Coef and Intercept)
#6. manual calculation

df['bedrooms'] = df['bedrooms'].fillna(df['bedrooms'].median())

X = df.drop('price', axis='columns')
y = df['price']

model = linear_model.LinearRegression()
model.fit(X,y)

#y = mx+c
print("Gradient(m): ", model.coef_)
print("Intercept(c): ", model.intercept_)



# #Predictions
model.predict([[3000,3,40]])

#Manual calculation
price = 3000*model.coef_[0] + 3*model.coef_[1] + 40*model.coef_[2] + model.intercept_



