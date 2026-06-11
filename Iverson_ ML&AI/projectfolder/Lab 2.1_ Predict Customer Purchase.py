import pandas as pd
import numpy as np


from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold,cross_val_score, GridSearchCV,RandomizedSearchCV
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression


df = pd.read_csv(".\\pandas\\customer_data.csv")

df.info()
df.shape

#pip install word2number --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Feature Engineering (LabelEncoder - change label data to number)
le =LabelEncoder()

df['martial_status_encoded'] = le.fit_transform(df['marital_status'])

df1 = df.drop('marital_status', axis=1)


X = df1.drop('purchase', axis='columns')
y = df['purchase']

# ==========================
# Hyperparameter Tuning - Grid Search
# ==========================

#Hyper parameter tuning
#Grid SearchCV (Cross Validation)
#RandomizeSearch
#Bayesian

param_grid = {
    "criterion":['gini','entrophy'],
    "max_depth":[None,3,5,10],
    "min_samples_split":[2,5,10],
    "min_samples_leaf":[1,2,4] }

grid_search = GridSearchCV(
    estimator=DecisionTreeClassifier(
        #random_state=42
    ),
    param_grid=param_grid,
    cv=5, #skf
    scoring="accuracy",
    #refit=True #dia auto model
    n_jobs=-1 #all processer in laptop -1 is the last one
)
grid_search.fit(X,y)

grid_search.best_params_
grid_search.best_score_
grid_search.best_estimator_

# #Manually Train
# best_param = grid_search.best_params_

# model = DecisionTreeClassifier(
#     random_state=42,
#     **best_param
# )
# model.fit(X,y)

#auto
bestModel = grid_search.best_estimator_
bestModel.predict([[35,5000,0]])

# ==========================
# NAN
# ==========================

# model = DecisionTreeClassifier(random_state=42)
# model2 = LogisticRegression(random_state=42)


# model.fit(X,y)

# # #Predictions
# model.predict([[30,5000,0]])

# ==========================
# Hyperparameter Tuning - Randomize Search
# ==========================

#randomize seacrh
# - n iter = 10 (10 combination)

param_dist = {
    "criterion":['gini','entrophy'],
    "max_depth":[None,3,5,10],
    "min_samples_split":[2,5,10],
    "min_samples_leaf":[1,2,4] }

random_search = RandomizedSearchCV(
    estimator=DecisionTreeClassifier(
        #random_state=42
    ),
    param_distributions=param_dist,
    n_iter=10, 
    cv=5,
    scoring="accuracy",
    refit=True, #dia auto model
    n_jobs=-1 #all processer in laptop -1 is the last one
)
random_search.fit(X,y)

random_search.best_params_
random_search.best_score_
random_search.best_estimator_

#auto
bestModel1 = random_search.best_estimator_
bestModel1.predict([[35,5000,0]])

# ==========================
# Train Test Split
# ==========================

#Train Test Split (model evaluation)
X_train, X_test, y_train, y_test = train_test_split(X,
                                                   y,
                                                    test_size=0.2,
                                                    stratify=y) # #random_state=42
model.fit(X_train,y_train)

prediction_train = model.predict([[30,5000,0]])


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


# ==========================
# Kfold  cross validation (buat 5 takup then train by takup)
# ==========================

# split dataset into kfold
# model is trained and tested 5 times
# the final score is the avg of the 5 run
# does not guarantee the same class distribution in every fold
# usually use in regression


kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
scores = cross_val_score(
    model,
    X,
    y,
    cv=kf,
    scoring='accuracy' #precision_macro, recall, f1
)
#compare against logistic regression
scores2 = cross_val_score(
    model2,
    X,
    y,
    cv=kf,
    scoring='accuracy' #precision_macro, recall, f1
)
scores
scores.mean()
scores2
scores2.mean()



# ==========================
# stratified Kfold  validation (Split target is stratified of ratio sme)
# ==========================
# split dataset into kfold
# model is trained and tested 5 times
# preserves the class distribution in every fold
# recommended approch for classification

skf = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
scores_s = cross_val_score(
    model,
    X,
    y,
    cv=skf,
    scoring='accuracy' #precision_macro, recall, f1
)
#compare against logistic regression
scores_s2 = cross_val_score(
    model2,
    X,
    y,
    cv=skf,
    scoring='accuracy' #precision_macro, recall, f1
)
scores_s
scores_s.mean()
scores_s2
scores_s2.mean()



# ==========================
# Decision Tree Visualisation
# ==========================

model.fit(X,y)

import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

plt.figure(figsize=(12, 8))
plot_tree(
    model,
    feature_names=X.columns,
    class_names=[str(cls) for cls in model.classes_],
    filled=True,
    rounded=True,
    fontsize=10
)
plt.title("Decision Tree Visualization")
plt.show()

#to save in png

# plt.figure(figsize=(12, 8))
# plot_tree(
#     model,
#     feature_names=X.columns,
#     class_names=[str(cls) for cls in model.classes_],
#     filled=True,
#     rounded=True,
#     fontsize=10
# )
# plt.title("Decision Tree Visualization")
# plt.savefig("decision_tree.png", dpi=300, bbox_inches='tight')
# plt.show()




