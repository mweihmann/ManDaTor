from flask import Flask
import pika
import json
import time
import random
from datetime import datetime
import threading

app = Flask(__name__)
user_running = False  # Prevent multiple starts

#delivers simulated energy usage (morning and evening)
def get_user_kwh():
    """Simulate energy usage based on time of day."""
    hour = datetime.now().hour
    base = random.uniform(0.001, 0.003)
    if 6 <= hour <= 9 or 17 <= hour <= 21:
        base *= 2  # Peak usage times: morning and evening
    return round(base, 6)

# sends every 5 seconds a USER message
def send_usage():
    """Send USER messages to RabbitMQ every 5 seconds."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='energy')

    print("[User] Started.")
    try:
        while True:
            message = {
                "type": "USER",
                "association": "COMMUNITY",
                "kwh": get_user_kwh(),
                "datetime": datetime.now().isoformat(timespec='seconds')
            }
            channel.basic_publish(
                exchange='',
                routing_key='energy',
                body=json.dumps(message)
            )
            print("[User] Sent:", message)
            time.sleep(5)
    except KeyboardInterrupt:
        print("[User] Stopped.")
    finally:
        connection.close()

@app.route('/start')
def start_user():
    global user_running
    if not user_running:
        thread = threading.Thread(target=send_usage, daemon=True)
        thread.start()
        user_running = True
        return "User started.\n"
    else:
        return "User is already running.\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)