from aiokafka import AIOKafkaProducer
import asyncio
import json

async def send(topic: str, key: str, value: dict):
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        await producer.send(topic, key=key.encode(), value=json.dumps(value).encode())
        print(f"Sent: {key} -> {value}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(send("orders", "order:1", {"product": "Hammer", "quantity": 5, "total": 175000}))
