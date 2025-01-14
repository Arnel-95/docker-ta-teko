# consumer/consumer.py
import os
import pika
import json
from pymongo import MongoClient

BATCH_SIZE = 1000
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME   = os.getenv("RABBITMQ_QUEUE", "AAPL")
MONGODB_URL  = os.getenv("MONGODB_URL", "mongodb://mongo1:27017/?replicaSet=rs0")

# Verbindung zu RabbitMQ
params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

# Verbindung zur MongoDB
client = MongoClient(MONGODB_URL)
collection = client["stockmarket"]["stocks"]

buffer = []

def callback(ch, method, properties, body):
    global buffer
    message = json.loads(body)
    buffer.append(message)
    
    if len(buffer) == BATCH_SIZE:
        # Aggregation
        total_price = sum([msg["price"] for msg in buffer])
        avg_price = total_price / BATCH_SIZE
        company = buffer[0]["company"]  # alle aus derselben Queue, also dieselbe Firma
        
        # Speichern in MongoDB
        doc = {"company": company, "avgPrice": float(avg_price)}
        collection.insert_one(doc)
        
        # Buffer leeren
        buffer = []
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=False
)

print(f" [*] Waiting for messages from queue '{QUEUE_NAME}'...")
channel.start_consuming()
