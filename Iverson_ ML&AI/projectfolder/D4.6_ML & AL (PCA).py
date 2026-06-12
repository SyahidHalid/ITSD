#dimensionality reduction
# 1 scale features before PCA
# Accuracy might drop

import pandas as pd
import matplotlib.pyplot    as plt

from sklearn.datasets import load_digits
from sklearn.preprocessing import   StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA

digits = load_digits()

digits.data.shape

df = pd.DataFrame(digits.data, columns=digits.feature_names )
df

plt.gray()
plt.matshow(digits.data[11].reshape(8,8))
plt.show

X = pd.DataFrame(digits.data, columns=digits.feature_names)
y = digits.target


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


#Apply PCA
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

X.shape[1]
X_pca.shape[1]



X_Train,X_Test,y_train,y_test = train_test_split(X_pca,y,test_size=0.2)

model = LogisticRegression()
model.fit(X_Train,y_train)

pca_accuracy = model.score(X_Test,y_test)
pca_accuracy





X_train_pca,X_test_pca,y_train,y_test = train_test_split(X_pca,y,test_size=0.2)

model = LogisticRegression()
model.fit(X_train_pca,y_train)

pca_accuracy = model.score(X_test_pca,y_test)
pca_accuracy



# model.predict_proba(X_test)

# y_predicted = model.predict(X_test)
# y_predicted

# #evaluate model accuracy
# accuracy = model.score(X_test, y_test)
# accuracy

# accuracy = model.score(X, y)
# accuracy

# accuracy2 = accuracy_score(y_test,y_predicted)
# accuracy2

