import os
from flask import Flask # Web server
import pika # RabbitMQ connection
import json
import time
import random
from datetime import datetime
import threading
import pytz

app = Flask(__name__)
stop_event = threading.Event() 
user_thread = None 


def get_user_kwh():
    """Simulate energy usage based on time of day."""
    hour = datetime.now().hour
    base = random.uniform(0.001, 0.003)
    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0)) 
    if 6 <= hour <= 9 or 17 <= hour <= 21:
        base *= 2  
    return round(base, 6)

def send_usage():
    """Send USER messages to RabbitMQ every 5 seconds."""
    while not stop_event.is_set():
        try:
            connection = connect_rabbitmq() 
            channel = connection.channel()
            channel.queue_declare(queue='energy')

            print("[User] Started.")
            
            while not stop_event.is_set():
                vienna_tz = pytz.timezone("Europe/Vienna")
                message = {
                    "type": "USER",
                    "association": "COMMUNITY",
                    "kwh": get_user_kwh(),
                    "datetime": datetime.now(vienna_tz).isoformat(timespec='seconds')
                }
                channel.basic_publish(
                    exchange='',
                    routing_key='energy',
                    body=json.dumps(message)
                )
                print("[User] Sent:", message)
                stop_event.wait(5)
        except Exception as e:
            print("[User] Error:", e)
            print("[User] Attempting reconnect in 5s...")
            time.sleep(5)
        finally:
            try:
                connection.close()
            except:
                pass


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


@app.route('/start')
def start_user():
    global user_thread
    if user_thread is None or not user_thread.is_alive():
        stop_event.clear()
        user_thread = threading.Thread(target=send_usage, daemon=True)
        user_thread.start()
        return "User started.\n"
    return "User is already running.\n"

@app.route('/stop')
def stop_user():
    stop_event.set()
    return "User stopping...\n"

if __name__ == '__main__':
    # Auto-start thread on container boot
    stop_event.clear()
    user_thread = threading.Thread(target=send_usage, daemon=True)
    user_thread.start()

    port = int(os.environ.get("PORT", 5004))
    app.run(host='0.0.0.0', port=port)