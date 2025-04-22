from flask import Flask
import pika
import json
import time
import random
from datetime import datetime
import threading

app = Flask(__name__)
producer_running = False  # prevents multiple starts

# delivers simulated solarenergy (midday)
def get_solar_kwh():
    """Simulated Solar-Production depending on time."""
    hour = datetime.now().hour
    base = random.uniform(0.002, 0.006)
    if 10 <= hour <= 16:
        base *= 1.5  # midday more sunlight
    return round(base, 6)

# sends every 5 seconds a producer message
def send_energy():
    """Sends PRODUCER-messages every 5 Seconds to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='energy')

    print("[Producer] Started.")
    try:
        while True:
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
            time.sleep(5)
    except KeyboardInterrupt:
        print("[Producer] stopped.")
    finally:
        connection.close()

# start the producer in a separate thread
@app.route('/start')
def start_producer():
    global producer_running
    if not producer_running:
        thread = threading.Thread(target=send_energy, daemon=True)
        thread.start()
        producer_running = True
        return "Producer was started.\n"
    else:
        return "Producer is already running.\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)