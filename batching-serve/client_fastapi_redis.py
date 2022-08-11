from typing import Optional

from fastapi import FastAPI, Body
import aioredis
import uuid
import json

app = FastAPI()
r = aioredis.from_url("redis://localhost", decode_responses=True)
TIMEOUT = 60 * 5

async def reader(channel: aioredis.client.PubSub, c_id: str) -> Optional[str]:
    # Wait for TIMEOUT second at most. # TODO Challenge one, with great traffic comes great timeout,
    # otherwise you will get loooots of connection error. How can we decide timeout value?
    message = await channel.get_message(ignore_subscribe_messages=True, timeout=TIMEOUT)
    if message:
        await channel.unsubscribe(c_id)
        await channel.close()
        return message["data"]


@app.post("/predict")
async def root(number: str = Body(..., embed=True)):
    # Create random ID
    unique_id = str(uuid.uuid4())

    # Publish message to predict topic
    message = json.dumps({"c_id": unique_id, "number": number})
    await r.publish("predict", message)

    # Wait for the response
    p = r.pubsub()
    await p.subscribe(unique_id)

    for i in range(3):
        result = await reader(p, unique_id)
        if result:
            return result
        # If we cannot get a response in 3 second, try to publish again
        await r.publish("predict", message)

    raise ConnectionError(
        "Cannot connect to the prediction server. Please try again later"
    )
