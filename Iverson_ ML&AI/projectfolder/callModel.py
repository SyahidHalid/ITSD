import joblib

model = joblib.load('../../DAY5/FASTAPI/MusicApi/app/model/music_recomender.job')
print(model.predict([[21,1]]))