import os
import pika
import json
from pymongo import MongoClient

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME   = os.getenv("RABBITMQ_QUEUE", "AAPL")
MONGODB_URL  = os.getenv("MONGODB_URL", "mongodb://localhost:27017/stockmarket")
BATCH_SIZE   = 1000

connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

client = MongoClient(MONGODB_URL)
db = client.get_database()     # z.B. "stockmarket"
collection = db["stocks"]

buffer = []

def process_batch(batch):
    total = sum(item["price"] for item in batch)
    avg_price = total / len(batch)
    company = batch[0]["company"]
    collection.insert_one({"company": company, "avgPrice": avg_price})

def callback(ch, method, properties, body):
    global buffer
    msg = json.loads(body)
    buffer.append(msg)

    if len(buffer) >= BATCH_SIZE:
        process_batch(buffer)
        buffer.clear()

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
print(f" [*] Wartet auf Nachrichten in Queue {QUEUE_NAME} ...")
channel.start_consuming()
