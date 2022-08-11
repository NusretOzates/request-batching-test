from fastapi import FastAPI, Body
from keras.models import load_model

app = FastAPI()

model = load_model("models/multiply_two")


@app.post("/predict")
async def root(number: str = Body(..., embed=True)):
    prediction = model.predict([int(number)]).tolist()[0][0]

    return {"message": prediction}
