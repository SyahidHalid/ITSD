from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os 

# pip install fastapi --trusted-host pypi.org --trusted-host files.pythonhosted.org
# pip install uvicorn --trusted-host pypi.org --trusted-host files.pythonhosted.org

#define INput data structure
class MusicInput(BaseModel):
    age: int
    gender: int

# initialize fastapi
app = FastAPI(
    title='music recommender API',
    description="A simple API that recommends music genre",
    version='1.0.0'
)

model_path = os.path.join(os.path.dirname(__file__),"model\\music_recommender.job") #model/music-recomender.job
model = joblib.load(model_path)

#create the home endpoint
@app.get("/")
def home():
    return {"message":"Welcome to the music recommender API",
            "desc":"Connection Sucessfully"}

# open terminal
#  D:\00. Git Repository\ITSD\Iverson_ ML&AI\projectfolder\musicAPI> uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --post 8001 --reload
# http://127.0.0.1:8000/docs click


@app.post("/predict")
def predict_music(data:MusicInput):
    prediction = model.predict([[data.age, data.gender]])
    return{
        'age':data.age,
        'gender':data.gender,
        'predcited_genre':prediction[0]
    }


