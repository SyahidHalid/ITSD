import pandas as pd
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn.inspection import permutation_importance

# pip install shap --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install "numpy<2" --trusted-host pypi.org --trusted-host files.pythonhosted.org
# import numpy as np
# print(np.__version__)

import shap

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



#feature importance
feature_importance = pd.DataFrame({
    'Features':X.columns,
    'Coefficient': model.coef_
})

feature_importance = feature_importance.sort_values(
    by='Coefficient',
    ascending=False
)
feature_importance

# Shap
explainer = shap.Explainer(
    model,
    X
)

shap_values = explainer(X)
shap_values

#plot global explaination
shap.summary_plot(
    shap_values,
    X
)

# individual explanation
shap.plots.waterfall(
    shap_values[0]
)