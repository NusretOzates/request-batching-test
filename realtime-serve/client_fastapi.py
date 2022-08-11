from fastapi import FastAPI, Body
import aiohttp

app = FastAPI()


@app.post("/predict")
async def root(number: str = Body(..., embed=True)):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8080/predict"
        async with session.post(url, json={"number": number}) as resp:
            return await resp.text()
