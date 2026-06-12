# Articial Neural Netwrok (ANN)
# CNN 
# RNN 
# transformer 

# pip list

import pandas as pd
import numpy as np

# pip install tensorflow --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install numpy --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install scikit-learn --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install matplotlib --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install pandas --trusted-host pypi.org --trusted-host files.pythonhosted.org


# pip install "tensorflow==2.16.2" --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip show tensorflow

# y = mx (wight in ANN) + c (bias in ANN)


import tensorflow as tf

from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold,cross_val_score, GridSearchCV,RandomizedSearchCV
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression


df = pd.read_csv("D:\\00. Git Repository\\ITSD\\Iverson_ ML&AI\\projectfolder\\pandas\\customer_data.csv")

df.info()
df.shape

#pip install word2number --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Feature Engineering (LabelEncoder - change label data to number)
le =LabelEncoder()

df['martial_status_encoded'] = le.fit_transform(df['marital_status'])

df['purchase_encoded'] = le.fit_transform(df['purchase'])

df1 = df.drop(['marital_status','purchase'], axis=1)


X = df1.drop('purchase_encoded', axis='columns')
y = df['purchase_encoded']

#Train Test Split (model evaluation)
X_train, X_test, y_train, y_test = train_test_split(X,
                                                   y,
                                                    test_size=0.2,
                                                    stratify=y) # #random_state=42


# model.fit(X_train,y_train)

# prediction_train = model.predict([[30,5000,0]])


#sambung script lain