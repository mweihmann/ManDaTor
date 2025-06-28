from flask import Flask # Web server
import pika # RabbitMQ connection
import json
import time
import random
from datetime import datetime
import threading
import os
from util.rabbitmq import connect_rabbitmq # Helper function to connect to RabbitMQ
import requests
import pytz


app = Flask(__name__)
producer_thread = None # Store reference to the running thread
stop_event = threading.Event() # Event to stop the thread

# Simulates solar energy production depending on time of day
def get_solar_kwh():
    """
    Simulates the current solar energy production in kWh.
    - Random value between 0.002 and 0.006 kWh (2–6 Wh)
    - Optionally scalable via the SOLAR_MULTIPLIER environment variable
    - Boosted in sunny weather using the weather API
    """

    # Base production: 2–6 Wh per measurement interval (e.g., 5 seconds)
    base = random.uniform(0.002, 0.006)

    # Local multiplier from environment variable (e.g., for testing)
    base *= float(os.environ.get("SOLAR_MULTIPLIER", 1.0))

    try:
        # Amplification depending on cloud cover + UV index (up to 1.5x)
        weather_factor = get_weather_cloud_factor()
        base *= weather_factor
    except Exception as e:
        print("[SolarKWH] Wetterfaktor konnte nicht berechnet werden:", e)

    return round(base, 6)  # z. B. 0.004832

# weather api to get current weather data and calculate a solar production factor
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

        # Request to WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}&aqi=no"
        response = requests.get(url, timeout=5)  # Timeout for network stability
        response.raise_for_status()  # Exception, if HTTP-Code not 200

        data = response.json()

        # extract UV-Index und cloudyness from the response
        uv_index = float(data["current"].get("uv", 0))               # z. B. 9.0
        cloud_percent = float(data["current"].get("cloud", 100))     # z. B. 25 %

        # Calculate the cloud factor:
        # - 0.0 at 100% clouds (no sun)
        # - 1.0 at 0% Clouds (maximale sun intensity)
        cloud_factor = max(0.0, min(1.0, 1.0 - cloud_percent / 100.0))

        # UV-Bonus (linear: till max. +50 %)
        # - 1.0 at UV-Index 0
        # - 1.5 at UV-Index 10
        # - capped at 1.5
        # - e.g. 0.0 at UV-Index 0, 1.0 at UV-Index 2, 1.5 at UV-Index 10
        uv_bonus = min(1.0 + (uv_index / 10.0) * 0.5, 1.5)

        return cloud_factor * uv_bonus  #example 0.75 × 1.4 = 1.05

    except Exception as e:
        print("[WeatherAPI] Error retrieving weather data:", e)
        return 1.0  # Fallback: keine Reduktion, normale Basisproduktion


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
                vienna_tz = pytz.timezone("Europe/Vienna")
                message = {
                    "type": "PRODUCER",
                    "association": "COMMUNITY",
                    "kwh": get_solar_kwh(),
                    "datetime": datetime.now(vienna_tz).isoformat(timespec='seconds')
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