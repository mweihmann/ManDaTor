from flask import Flask # Web server
import pika # RabbitMQ connection
import json
import time
import random
from datetime import datetime
import threading
import os
from util.rabbitmq import connect_rabbitmq # Helper function to connect to RabbitMQ

app = Flask(__name__)
producer_thread = None # Store reference to the running thread
stop_event = threading.Event() # Event to stop the thread

# Simulates solar energy production depending on time of day
def get_solar_kwh():
    """ 
    Returns a simulated amount of produced energy in kWh.
    Production is higher between 10 AM and 4 PM.
    The amount can be influenced by the environment variable "SOLAR_MULTIPLIER".
    """
    hour = datetime.now().hour
    base = random.uniform(0.002, 0.006) # Random base between 2–6 Wh (0.002–0.006 kWh)
    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0)) # default multiplier from yml file env variable
    if 10 <= hour <= 16:
        base *= 1.5 # Increase output during peak solar hours (50% more)
    return round(base, 6)

# sends every 5 seconds a producer message 
def send_energy():
    """ 
    Sends a PRODUCER message to RabbitMQ every 5 seconds.
    Each message includes: type, association (COMMUNITY), current production in kWh, and timestamp.
    If a connection error occurs, the system will retry every 5 seconds.
    """
    while not stop_event.is_set():
        try:            
            connection = connect_rabbitmq() # connect to RabbitMQ
            channel = connection.channel()
            channel.queue_declare(queue='energy') # Ensure the "energy" queue exists

            print("[Producer] Started.")
            while not stop_event.is_set(): # could also be while true instead of stop event
                # Build the message payload
                message = {
                    "type": "PRODUCER",
                    "association": "COMMUNITY",
                    "kwh": get_solar_kwh(),
                    "datetime": datetime.now().isoformat(timespec='seconds')
                }
                channel.basic_publish( # Send the message to RabbitMQ
                    exchange='',
                    routing_key='energy',
                    body=json.dumps(message)
                )
                print("[Producer] Sent:", message)
                stop_event.wait(5)  # Wait 5 seconds or exit early if stop_event is triggered
        except Exception as e: # Handle connection errors and try again
            print("[Producer] Error:", e)
            print("[Producer] Attempting reconnect in 5s...")
            time.sleep(5)
        finally: # Cleanly close the connection
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

# stop the producer manually in a separate thread
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