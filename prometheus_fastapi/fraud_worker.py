from kafka import KafkaConsumer
from fraud_detection import check_circular_fraud, register_ownership
import json

print("Fraud detection worker started — listening on fraud.check.queue...")

consumer = KafkaConsumer(
    'fraud.check.queue',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='fraud-detection-group'
)

for message in consumer:
    data = message.value
    print(f"Processing fraud check for {data['land_id']}...")

    # Register ownership in Neo4j
    register_ownership(
        plot_id=data['land_id'],
        owner_name=data['owner_name'],
        national_id=data['national_id'],
        amount=data['amount'],
        date=data['date']
    )

    # Run deep fraud detection
    result = check_circular_fraud(data['national_id'])

    if result['fraud_detected']:
        print(f"🚨 FRAUD DETECTED: {data['land_id']} — "
              f"risk level: {result['risk_level']}")
        print(f"   Chain: {result['transfer_dates']}")
        print(f"   Amounts: {result['amounts']}")
    else:
        print(f"✅ Clean: {data['land_id']} passed fraud check")