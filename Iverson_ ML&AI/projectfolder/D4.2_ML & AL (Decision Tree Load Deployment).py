import joblib

model = joblib.load("music_recommender.job")

model.predict([[21,1]])