from aiokafka import AIOKafkaConsumer
import asyncio
import json

async def main():
    consumer = AIOKafkaConsumer(
        "stock-updates", bootstrap_servers="localhost:9092",
        group_id="stock-notifier"
    )
    await consumer.start()
    print("Stock notification worker running. Waiting for events...")
    try:
        async for msg in consumer:
            event = json.loads(msg.value)
            print(f"[NOTIFICATION] Product {event['product_id']} stock changed to {event['quantity']} by {event['updated_by']}")
            # In real app: send email, SMS, or push notification here
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
