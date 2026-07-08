import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe("stock-notifications")
print("Redis notifier running. Waiting for events...")

for msg in pubsub.listen():
    if msg["type"] == "message":
        event = json.loads(msg["data"])
        print(f"[NOTIFICATION] Product {event['product_id']} stock changed to {event['quantity']}")
        # In real app: send email, SMS, or push notification here
