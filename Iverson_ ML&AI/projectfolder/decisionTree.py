import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.model_selection import train_test_split
import joblib
import graphviz

#Import Data
df = pd.read_csv('music.csv')
print(df)

#Seperate for Features and target
X = df.drop(columns=['genre'])
y = df['genre']

#Create a Model
model = DecisionTreeClassifier()
# X_train , X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, )
# model.fit(X_train,y_train)
model.fit(X,y)

# #Evaluate
# prediction = model.predict(X_test)
# print(accuracy_score(y_test, prediction))

joblib.dump(model, "../../DAY5/FASTAPI/MusicApi/app/model/music_recomender.job")

dot_data = tree.export_graphviz(
    model,
    out_file=None,  # keep this None to get a string instead of writing to file (out_file = 'music_recommender.dot)
    feature_names=['age', 'gender'],
    class_names=sorted(y.unique()),
    label='all',
    rounded=True,
    filled=True
)

graph = graphviz.Source(dot_data)
graph.render("musicRecommenderTree", format='png', cleanup=True)
graph.view()

