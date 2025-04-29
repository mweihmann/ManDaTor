from flask import Flask
import pika
import json
import time
import random
from datetime import datetime
import threading
import os
from util.rabbitmq import connect_rabbitmq

app = Flask(__name__)
producer_thread = None # Store reference to the running thread
stop_event = threading.Event() # Event to stop the thread

# delivers simulated solarenergy (midday)
def get_solar_kwh():
    """Simulated Solar-Production depending on time."""
    hour = datetime.now().hour
    base = random.uniform(0.002, 0.006)
    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0)) # default multiplier from yml file env variable
    if 10 <= hour <= 16:
        base *= 1.5
    return round(base, 6)

# sends every 5 seconds a producer message
def send_energy():
    """Sends PRODUCER-messages every 5 Seconds to RabbitMQ."""
    while not stop_event.is_set():
        try:            
            connection = connect_rabbitmq() # connect to RabbitMQ
            channel = connection.channel()
            channel.queue_declare(queue='energy')

            print("[Producer] Started.")
            while not stop_event.is_set(): # could also be while true instead of stop event
                message = {
                    "type": "PRODUCER",
                    "association": "COMMUNITY",
                    "kwh": get_solar_kwh(),
                    "datetime": datetime.now().isoformat(timespec='seconds')
                }
                channel.basic_publish(
                    exchange='',
                    routing_key='energy',
                    body=json.dumps(message)
                )
                print("[Producer] Sent:", message)
                stop_event.wait(5)  # wait for 5 seconds or until the event is set
        except Exception as e:
            print("[Producer] Error:", e)
            print("[Producer] Attempting reconnect in 5s...")
            time.sleep(5)
        finally:
            try:
                connection.close()
                print("[Producer] Stopped.")
            except:
                pass    

# start the producer manually in a separate thread
@app.route('/start')
def start_producer():
    global producer_thread
    if producer_thread is None or not producer_thread.is_alive():
        stop_event.clear()
        producer_thread = threading.Thread(target=send_energy, daemon=True)
        producer_thread.start()
        return "Producer started.\n"
    return "Producer is already running.\n"
    
@app.route('/stop')
def stop_producer():
    stop_event.set()
    return "Producer stopping...\n"

if __name__ == '__main__':
    # Auto-start on container boot
    stop_event.clear()
    producer_thread = threading.Thread(target=send_energy, daemon=True)
    producer_thread.start()

    port = int(os.environ.get("PORT", 5004))
    app.run(host='0.0.0.0', port=port)