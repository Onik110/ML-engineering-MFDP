import pika
import json
import os


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_VIRTUAL_HOST = os.getenv("RABBITMQ_VIRTUAL_PORT", "/")

# Параметры подключения
connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,  
    port=RABBITMQ_PORT,          
    virtual_host=RABBITMQ_VIRTUAL_HOST,  
    credentials=pika.PlainCredentials(
        username=RABBITMQ_USER,  
        password=RABBITMQ_PASS  
    ),
    heartbeat=30,
    blocked_connection_timeout=60
)

def send_task(task_data: dict):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    queue_name = 'ml_task'
    channel.queue_declare(queue=queue_name, durable=True)

    message = json.dumps(task_data)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message
    )
    connection.close()