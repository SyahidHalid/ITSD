import pandas as pd
import numpy as np


from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold,cross_val_score, GridSearchCV,RandomizedSearchCV
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import RandomForestClassifier

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


model = RandomForestClassifier(
    n_estimators=10
    )

skf = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    #random_state=42
)
scores_s = cross_val_score(
    model,
    X,
    y,
    cv=skf,
    scoring='accuracy' #precision_macro, recall, f1
)

scores_s
scores_s.mean()

model.fit(X,y)

# tgk tree satu2
tree = model.estimators_[1]

from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plot_tree(
    tree,
    feature_names=X.columns,
    class_names=[str(cls) for cls in model.classes_],
    filled=True,
    rounded=True,
    fontsize=10
)
plt.title("Decision Tree from Random Forest")
plt.show()

