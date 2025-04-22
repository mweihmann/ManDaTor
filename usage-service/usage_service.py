
from flask import Flask
import pika, json, psycopg2
from datetime import datetime
from dateutil import parser
from database.util.db import get_connection

app = Flask(__name__)

# check that here is data for every hour
def ensure_hour_exists(cur, hour):
    cur.execute(
        "INSERT INTO usage_stats (hour, community_produced, community_used, grid_used) "
        "VALUES (%s, 0, 0, 0) "
        "ON CONFLICT (hour) DO NOTHING",
        (hour,)
    )

# called with every message from the queue
def process_message(ch, method, properties, body):
    data = json.loads(body)
    msg_type = data['type']
    kwh = float(data['kwh'])
    dt = parser.isoparse(data['datetime']) # convert ISO-time string into datetime
    hour = dt.replace(minute=0, second=0, microsecond=0) #round to hours

    conn = get_connection()
    cur = conn.cursor()

    ensure_hour_exists(cur, hour)

    # producer increasing energy elif user needs energy
    if msg_type == "PRODUCER":
        cur.execute("UPDATE usage_stats SET community_produced = community_produced + %s WHERE hour = %s", (kwh, hour))
    elif msg_type == "USER":
        cur.execute("SELECT community_produced, community_used FROM usage_stats WHERE hour = %s", (hour,))
        result = cur.fetchone()

        if result is None:
            print(f"No data found for hour: {hour}")
            conn.close()
            return
        
        produced = float(result["community_produced"])
        used = float(result["community_used"])
        available = produced - used
        grid_add = max(0, kwh - available)
        cur.execute("UPDATE usage_stats SET community_used = community_used + %s, grid_used = grid_used + %s WHERE hour = %s", (kwh, grid_add, hour))

    conn.commit()
    cur.close()
    conn.close()
# create background thread which waits for rabbitmq messages
@app.route('/start')
def start():
    import threading
    def listen():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='energy')
        channel.basic_consume(queue='energy', on_message_callback=process_message, auto_ack=True)
        print("Usage Service started. Listening for messages...")
        channel.start_consuming()

    thread = threading.Thread(target=listen)
    thread.start()
    return "Usage Service started."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
