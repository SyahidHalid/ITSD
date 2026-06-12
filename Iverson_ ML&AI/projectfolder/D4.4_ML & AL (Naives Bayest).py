import pandas as pd
import numpy as np

from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

df = pd.read_csv(".\\pandas\\train.csv")

df.info()
df.shape

df[df.columns[6]].value_counts()

#P(A|B) = (P(B|A) * P(A) )/ P(B)

# A = survived
# B = female

# what is the probability that a passenger survived given the passenger is female?

# total passenger = 891
# Survived = 342
# Female = 314
# Female and survived = 233

# P(Survived) = 342/891 = 0.3
# P(Female|Survived) = 233/342 = 0.6
# P(Female) = 314/891 = 0.3

# P(Survived|Female) = 0.6821 * 0.384 / 0.352 = 0.

le =LabelEncoder()

df['sex_encoded'] = le.fit_transform(df['sex'])

#df['pclass']

df['age'] = df['age'].fillna(df['age'].mean())

#df['fare']

df1 = df.drop(['name',
         'ticket',
         'cabin',
         'embarked',
         'sex',
         'sibsp',
         'parch'], axis='columns')

X = df1.drop('survived', axis='columns')
y = df1['survived']

X_train, X_test, y_train, y_test = train_test_split(X,
                                                   y,
                                                    test_size=0.2,
                                                    stratify=y,
                                                    random_state=42) # #

model = GaussianNB()
model.fit(X_train, y_train)
accuracy = model.score(X_test,y_test)
accuracy

print(X_test[:10])

prediction = model.predict(X_test[:10])
prediction

probabilities = model.predict_proba(
    X_test[:10]
)
probabilities



