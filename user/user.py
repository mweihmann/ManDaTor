import os
from flask import Flask # Web server
import pika # RabbitMQ connection
import json
import time
import random
from datetime import datetime
import threading
from util.rabbitmq import connect_rabbitmq
import pytz

app = Flask(__name__)
stop_event = threading.Event()  # Event to stop the thread
user_thread = None  # Store reference to the running thread

# This function simulates energy usage (kWh)
# More usage in morning (6–9) and evening (17–21)
def get_user_kwh():
    """Simulate energy usage based on time of day."""
    hour = datetime.now().hour
    base = random.uniform(0.001, 0.003)
    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0)) # default multiplier from yml file env variable
    if 6 <= hour <= 9 or 17 <= hour <= 21:
        base *= 2  # Higher energy usage during typical peak hours
    return round(base, 6)

# sends every 5 seconds a USER message
def send_usage():
    """Send USER messages to RabbitMQ every 5 seconds."""
    while not stop_event.is_set():
        try:
            connection = connect_rabbitmq() # connect to RabbitMQ
            channel = connection.channel()
            channel.queue_declare(queue='energy')

            print("[User] Started.")
            
            while not stop_event.is_set():  # could also be while true instead of stop event
                vienna_tz = pytz.timezone("Europe/Vienna")
                message = {
                    "type": "USER",
                    "association": "COMMUNITY",
                    "kwh": get_user_kwh(),
                    "datetime": datetime.now(vienna_tz).isoformat(timespec='seconds')
                }
                channel.basic_publish(  # send message to RabbitMQ
                    exchange='',
                    routing_key='energy',
                    body=json.dumps(message)
                )
                print("[User] Sent:", message)
                stop_event.wait(5) # wait for 5 seconds or until the event is set
        except Exception as e:
            print("[User] Error:", e)
            print("[User] Attempting reconnect in 5s...")
            time.sleep(5)
        finally:
            try:
                connection.close()
            except:
                pass

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