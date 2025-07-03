from flask import Flask
import pika, json, psycopg2, threading
from datetime import datetime
from dateutil import parser
import time
import os
from psycopg2.extras import RealDictCursor
from datetime import timezone

app = Flask(__name__)
usage_thread = None
stop_event = threading.Event()

# check that here is data for every hour
def ensure_hour_exists(cur, hour):    
    print(f"[Usage Service] Ensuring hour exists: {hour}")
    cur.execute(
        "INSERT INTO usage_stats (hour, community_produced, community_used, grid_used) "
        "VALUES (%s, 0, 0, 0) "
        "ON CONFLICT (hour) DO NOTHING",
        (hour,)
    )

# called with every message from the queue
def process_message(ch, method, properties, body):
    print("[Usage Service] Received message:", body)
    data = json.loads(body)
    msg_type = data['type']
    kwh = float(data['kwh'])
    
    
    dt = parser.isoparse(data['datetime']) # convert ISO-time string into datetime

    hour = dt.replace(minute=0, second=0, microsecond=0)
    
    #  Open database connection
    conn = get_connection()
    cur = conn.cursor()

    # Make sure that this hour exists in the database
    ensure_hour_exists(cur, hour)

    # producer increasing energy elif user needs energy
    if msg_type == "PRODUCER":
        print(f"[Usage Service] Processing PRODUCER message for hour: {hour}, kWh: {kwh}")
        cur.execute("UPDATE usage_stats SET community_produced = community_produced + %s WHERE hour = %s",
                    (kwh, hour)
                    )
    elif msg_type == "USER":
        print(f"[Usage Service] Processing USER message for hour: {hour}, kWh: {kwh}") 
        cur.execute("SELECT community_produced, community_used FROM usage_stats WHERE hour = %s",
                    (hour,)
                    )
        result = cur.fetchone()

        if result is None:
            print(f"No data found for hour: {hour}")
            conn.close()
            return
        
        produced = float(result["community_produced"])
        used = float(result["community_used"])
        available = produced - used
        grid_add = max(0, kwh - available)
        cur.execute("UPDATE usage_stats SET community_used = community_used + %s, grid_used = grid_used + %s WHERE hour = %s",
                    (kwh, grid_add, hour)
                    )

    conn.commit()
    cur.close()
    conn.close()

def listen():
    """Background thread: Connects to RabbitMQ and consumes messages."""
    while not stop_event.is_set():
        try:
            connection = connect_rabbitmq()
            channel = connection.channel()
            channel.queue_declare(queue='energy')
            channel.basic_consume(queue='energy', on_message_callback=process_message, auto_ack=True)
            print("Usage Service started. Listening for messages...")

            while not stop_event.is_set():
                connection.process_data_events(time_limit=1)
                stop_event.wait(1)
        except Exception as e:
            print("[Usage Service] Error connecting or processing:", e)
            print("[Usage Service] Retrying in 3 seconds...")
            stop_event.wait(3)
        finally:
            try:
                if connection and not connection.is_closed:
                    connection.close()
                    print("[Usage Service] Connection closed.")
            except Exception as e:
                print("[Usage Service] Error closing connection:", e)

def get_connection(retries=10, delay=3):

    for i in range(retries):
        try:
            return psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST", "database"),
                port=os.getenv("DB_PORT", 5432),
                cursor_factory=RealDictCursor
            )

        except psycopg2.OperationalError as e:
            print(f"[Postgres Retry {i+1}/{retries}] {e}")
            time.sleep(delay)

    raise Exception("Could not connect to PostgreSQL after multiple attempts.")


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

# create background thread which waits for rabbitmq messages
@app.route('/start')
def start():
    global usage_thread
    if usage_thread is None or not usage_thread.is_alive():
        stop_event.clear()
        usage_thread = threading.Thread(target=listen, daemon=True)
        usage_thread.start()
        return "Usage service started.\n"
    return "Usage service already running.\n"

@app.route('/stop')
def stop_usage():
    stop_event.set()
    return "Usage service stopping...\n"

if __name__ == '__main__':
    stop_event.clear()
    usage_thread = threading.Thread(target=listen, daemon=True)
    usage_thread.start()
    app.run(host='0.0.0.0', port=5007)