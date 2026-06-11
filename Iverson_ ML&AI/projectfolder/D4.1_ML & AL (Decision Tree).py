# enrtropy
# measure of randomness or impurity in a dataset

# facebook = YES (Entrophy Low)
# Google = Maximum Randomnes (Entrophy High)

# Information Gain = How much entrophy is reduced after a split

# Gini Impurity 
# 


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from sklearn import tree
import graphviz
import math

#Import Data
df = pd.read_csv(".\\pandas\\music.csv")

df.info()
df.shape

#pip install graphviz --trusted-host pypi.org --trusted-host files.pythonhosted.org


#Seperate for features and target
X = df.drop('genre', axis='columns')
y = df['genre']

#Create model
model = DecisionTreeClassifier()
model.fit(X,y)

prediction = model.predict([[21,1]])


#Train Test Split (model evaluation)
X_train, X_test, y_train, y_test = train_test_split(X,
                                                   y,
                                                    test_size=0.2) #stratify='y' #random_state=42
model.fit(X_train,y_train)

prediction_train = model.predict([[21,1]])


#score & accuracy

#model.predict_proba(X_test)

#teka y base on train model
y_predicted = model.predict(X_test)
y_predicted

#tgk score train model
accuracy = model.score(X_test, y_test)
accuracy

#tgk score 100% dataset
accuracy1 = model.score(X, y)
accuracy1

#compare y train model and y predicted 
accuracy2 = accuracy_score(y_test,y_predicted)
accuracy2

#===============================================

#bila dah puas hati validate kita deploy
model.fit(X,y)

#extract to job file
joblib.dump(model,"music_recommender.job")



#visualize

dot_data = tree.export_graphviz(model,
    out_file=None,
    feature_names=['age','gender'],
    class_names=sorted(y.unique()),
    label='all',
    rounded=True,
    filled=True
)

graph = graphviz.Source(dot_data)
graph.render("musicRecommenderTree",format='png',cleanup=True)
graph.view()

