from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_fraud_check(verification_id: str, land_id: str, 
                         owner_name: str, national_id: str, 
                         amount: float, date: str):
    """
    Publish a fraud check request to Kafka.
    Called after basic verification passes.
    """
    message = {
        "verification_id": verification_id,
        "land_id": land_id,
        "owner_name": owner_name,
        "national_id": national_id,
        "amount": amount,
        "date": date
    }
    producer.send('fraud.check.queue', value=message)
    producer.flush()
    print(f"Published fraud check for {land_id} to Kafka")