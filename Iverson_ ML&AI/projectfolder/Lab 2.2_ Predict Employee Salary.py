import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
import math

df = pd.read_csv(".\\pandas\\hiring.csv")

df.info()
df.shape

#pip install word2number --trusted-host pypi.org --trusted-host files.pythonhosted.org
from word2number import w2n

df['experience'].fillna('0',inplace=True)

df['experience'] = df['experience'].apply(w2n.word_to_num)

df['test_score(out of 10)'] = df['test_score(out of 10)'].fillna(math.floor(df['test_score(out of 10)'].mean()))

X = df.drop('salary($)', axis='columns')
y = df['salary($)']

model = linear_model.LinearRegression()
model.fit(X,y)

#y = mx+c
print("Gradient(m): ", model.coef_)
print("Intercept(c): ", model.intercept_)



# #Predictions
model.predict([[2,9,6]])
model.predict([[12,10,10]])

#Manual calculation
price = 2*model.coef_[0] + 9*model.coef_[1] + 6*model.coef_[2] + model.intercept_




