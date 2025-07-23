from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import threading
import json

app = FastAPI()

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

class Transaction(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(data: Transaction):
    scaled = scaler.transform([data.features])
    prediction = model.predict(scaled)
    return {"prediction": int(prediction[0])}

# Kafka Streaming (optional for real-time)
def kafka_stream():
    consumer = KafkaConsumer(
        "transactions",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        group_id="fraud-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )
    for msg in consumer:
        features = msg.value["features"]
        scaled = scaler.transform([features])
        pred = int(model.predict(scaled)[0])
        output = {"features": features, "prediction": pred}
        producer.send("predictions", output)

threading.Thread(target=kafka_stream, daemon=True).start()
