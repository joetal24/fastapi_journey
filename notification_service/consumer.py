from aiokafka import AIOKafkaConsumer
import asyncio
import json

async def listen(topic: str):
    consumer = AIOKafkaConsumer(topic, bootstrap_servers="localhost:9092")
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Received: key={msg.key.decode()}, value={json.loads(msg.value)}")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(listen("orders"))
