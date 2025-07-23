from kafka import KafkaConsumer
consumer = KafkaConsumer("predictions", bootstrap_servers="localhost:9092")
for msg in consumer:
    print(msg.value)
