from flask import Flask
import pika
import json
import time
import random
from datetime import datetime
import threading
import os
import requests


app = Flask(__name__)
producer_thread = None 
stop_event = threading.Event()

def get_solar_kwh():
    """
    Simulates the current solar energy production in kWh.
    - Random value between 0.002 and 0.006 kWh (2–6 Wh)
    - Optionally scalable via the SOLAR_MULTIPLIER environment variable
    - Boosted in sunny weather using the weather API
    """

    base = random.uniform(0.002, 0.006)

    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0))

    try:
        weather_factor = get_weather_cloud_factor()
        base *= weather_factor
    except Exception as e:
        print("[SolarKWH] Wetterfaktor konnte nicht berechnet werden:", e)

    return round(base, 6)  # z. B. 0.004832


def get_weather_cloud_factor():
    """
    Ruft aktuelle Wetterdaten von WeatherAPI ab und berechnet einen Produktionsfaktor:
    - 1.0 bei maximaler Sonnenintensität
    - reduziert bei Bewölkung
    - UV-Index erhöht den Faktor je nach Sonnenstärke (max. 1.5-fach)
    Gibt 0.0 zurück bei Fehlern (z. B. keine Verbindung oder ungültige Antwort).
    """

    try:
        # API-Key & location from .env/docker-compose or fallback
        API_KEY = os.environ.get("WEATHER_API_KEY", "cafdf43fa4944f6c9ac114249252806")
        LOCATION = os.environ.get("WEATHER_CITY", "Vienna")

        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}&aqi=no"
        response = requests.get(url, timeout=5) 
        response.raise_for_status()

        data = response.json()


        uv_index = float(data["current"].get("uv", 0))
        cloud_percent = float(data["current"].get("cloud", 100))

        cloud_factor = max(0.0, min(1.0, 1.0 - cloud_percent / 100.0))

        uv_bonus = min(1.0 + (uv_index / 10.0) * 0.5, 1.5)

        return cloud_factor * uv_bonus 

    except Exception as e:
        print("[WeatherAPI] Error retrieving weather data:", e)
        return 1.0 


def send_energy():
    """ 
    Sends a PRODUCER message to RabbitMQ every 5 seconds.
    Each message includes: type, association (COMMUNITY), current production in kWh, and timestamp.
    If a connection error occurs, the system will retry every 5 seconds.
    """
    while not stop_event.is_set():
        try:            
            connection = connect_rabbitmq(host="rabbitmq")
            channel = connection.channel()
            channel.queue_declare(queue='energy')

            print("[Producer] Started.")
            while not stop_event.is_set():

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
                stop_event.wait(5)
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