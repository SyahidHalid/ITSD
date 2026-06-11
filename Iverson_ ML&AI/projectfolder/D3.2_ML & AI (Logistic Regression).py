
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
#from sklearn import linear_model

import math

df = pd.read_csv(".\\pandas\\insurance_data.csv")

df.info()

# #1. handle missing values
# #2. create a feature and target
# #3. train multivariate linear regression
# #4. do predictions
# #5. model parameter (Coef and Intercept)
# #6. manual calculation

#visualise
plt.scatter(df.age,df.bought_insurance,marker="+",color="red")
plt.xlabel("age")
plt.ylabel("bought")
plt.title("age vs bought")
plt.show()

# y = 1/(1+e^-(mx+c))
X = df.drop('bought_insurance', axis='columns')
y = df['bought_insurance']

model = LogisticRegression()
model.fit(X,y)

print("Gradient(m): ", model.coef_)
print("Intercept(c): ", model.intercept_)

model.predict([[60]])

#Manual calculation

def sigmoid(x):
    return 1 / (1 + math.exp(-(x*model.coef_[0]+model.intercept_)))

print(sigmoid(60))


#Train Test Split (model evaluation)
X_train, X_test, y_train, y_test = train_test_split(df[['age']],
                                                    df['bought_insurance'],
                                                    test_size=0.2) #random_state=42
model.fit(X_train,y_train)

print("Gradient(m): ", model.coef_)
print("Intercept(c): ", model.intercept_)


# # #Predictions
model.predict([[60]])

#Manual calculation

def sigmoid(x):
    return 1 / (1 + math.exp(-(x*model.coef_[0]+model.intercept_)))

print(sigmoid(60))


#==========================================================================


model.predict_proba(X_test)

y_predicted = model.predict(X_test)
y_predicted

#evaluate model accuracy
accuracy = model.score(X_test, y_test)
accuracy

accuracy = model.score(X, y)
accuracy

accuracy2 = accuracy_score(y_test,y_predicted)
accuracy2


#==========================================================================


# z = mx + c
# m = coefficient
# c = intercept
# x = is age (features)
# z = score (not prediction yet)

# then LogisticRegression applies(z) to convert
# z into a probability

#kena amik coefficient lps train bru x meniru

import numpy as np
import matplotlib.pyplot as plt

# Your existing scatter plot
plt.scatter(df.age, df.bought_insurance, marker="+", color="red")

#==========================================================================

#kena apply tiap point punye porbability bru leh buat sigmoid
# # Define sigmoid function

df.age = df.age.astype(float)

import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-(x * model.coef_[0][0] + model.intercept_[0])))

df["bought_insurance_sigmoid"] = sigmoid(df["age"])


# # Plot sigmoid line
#plt.scatter(df.age, df.bought_insurance_sigmoid, color="blue", linewidth=2)
plt.plot(df.age, df.bought_insurance_sigmoid, color="blue", linewidth=2)

#==========================================================================

# Labels
plt.xlabel("age")
plt.ylabel("bought")
plt.title("age vs bought (with sigmoid)")
plt.show()

