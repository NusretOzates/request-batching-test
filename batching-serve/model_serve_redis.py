from keras.models import load_model
import aioredis
import json
import asyncio

model = load_model("../models/multiply_two")
r = aioredis.from_url("redis://localhost", decode_responses=True)

incoming_requests = []


def make_predictions():
    numbers = [int(number) for c_id, number in incoming_requests]
    predictions = model.predict(numbers).tolist()
    return predictions


async def return_responses(predictions: list):
    for prediction, (c_id, number) in zip(predictions, incoming_requests):
        await r.publish(c_id, prediction[0])

    incoming_requests.clear()


async def main():
    n = 32
    # To not call len(incoming_requests) everytime we have a request
    request_count = 0

    p = r.pubsub()
    await p.subscribe("predict")
    print("Model ready to work")
    while True:
        message = await p.get_message(ignore_subscribe_messages=True)
        if message:
            data = json.loads(message["data"])
            c_id, number = data["c_id"], data["number"]
            incoming_requests.append((c_id, number))
            request_count += 1
            if request_count == n:
                predictions = make_predictions()
                await return_responses(predictions)
                request_count = 0
        await asyncio.sleep(0.01)


if __name__ == "__main__":
    asyncio.run(main())
