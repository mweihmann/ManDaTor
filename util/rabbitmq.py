import pika
import time

def connect_rabbitmq(retries=10, delay=3, host='rabbitmq'):
    """
    Tries to connect to RabbitMQ with retries.
    """
    for i in range(retries):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except pika.exceptions.AMQPConnectionError:
            print(f"[RabbitMQ Retry {i+1}/{retries}] Not ready. Retrying in {delay}s...")
            time.sleep(delay)
    raise Exception("Could not connect to RabbitMQ after multiple attempts.")