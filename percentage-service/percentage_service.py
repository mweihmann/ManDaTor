from flask import Flask, jsonify
import psycopg2, threading
from datetime import datetime
import os
import time
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

stop_event = threading.Event()
percentage_thread = None

latest_data = {}

# Function to continuously update the latest percentage values every 5 seconds
def update_percentage_loop():
    print("[Percentage-Service] Starting percentage update loop...")

    global latest_data
    while not stop_event.is_set():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT hour, community_produced, community_used, grid_used 
                FROM usage_stats 
                ORDER BY hour DESC 
                LIMIT 1
            """)
            result = cur.fetchone()

            if result:
                hour = result["hour"]
                produced = float(result["community_produced"])
                used = float(result["community_used"])
                grid = float(result["grid_used"])

                # Compute percentages
                depleted = min(100.0, round((used / produced) * 100, 2)) if produced > 0 else 100.0
                grid_portion = round((grid / used) * 100, 2) if used > 0 else 0.0

                latest_data = {
                    "hour": hour.isoformat(),
                    "community_depleted": depleted,
                    "grid_portion": grid_portion
                }

                # Insert or update into usage_stats_percentage
                cur.execute("""
                    INSERT INTO usage_stats_percentage (hour, community_depleted, grid_portion)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (hour)
                    DO UPDATE SET 
                        community_depleted = EXCLUDED.community_depleted,
                        grid_portion = EXCLUDED.grid_portion
                """, (hour, depleted, grid_portion))

                conn.commit()
            else:
                latest_data = {}

            cur.close()
            conn.close()
        except Exception as e:
            print("[Percentage-Service] Error:", e)
            print("[Percentage-Service] Will retry in 5 seconds...")
        stop_event.wait(5)

# Database connection with retry logic
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

# API endpoint to get the latest percentages
@app.route('/percentage')
def percentage():
    if latest_data:
        return jsonify(latest_data)
    return jsonify({"error": "No data available"}), 404

# Start the background thread
@app.route('/start')
def start_percentage_service():
    global percentage_thread
    if percentage_thread is None or not percentage_thread.is_alive():
        stop_event.clear()
        percentage_thread = threading.Thread(target=update_percentage_loop, daemon=True)
        percentage_thread.start()
        return "Percentage service started.\n"
    return "Percentage service already running.\n"

# Stop the background thread
@app.route('/stop')
def stop_percentage_service():
    stop_event.set()
    return "Percentage service stopping...\n"

# Run the app
if __name__ == '__main__':
    stop_event.clear()
    percentage_thread = threading.Thread(target=update_percentage_loop, daemon=True)
    percentage_thread.start()
    app.run(host='0.0.0.0', port=5008)
