from flask import Flask, jsonify
import psycopg2, threading
from datetime import datetime
from util.db import get_connection

app = Flask(__name__)

stop_event = threading.Event()
percentage_thread = None

latest_data = {}

# delivers the newest percentages: how much energy was taken from the network vs community
def update_percentage_loop():
    """Continuously updates the latest percentage values every 5 seconds."""
    global latest_data
    while not stop_event.is_set():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT hour, community_produced, community_used, grid_used FROM usage_stats ORDER BY hour DESC LIMIT 1")
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                hour = result["hour"]
                produced = float(result["community_produced"])
                used = float(result["community_used"])
                grid = float(result["grid_used"])

                # amount of energy taken from the grid (if something was produced)
                depleted = min(100.0, round((used / produced) * 100, 2)) if produced > 0 else 100.0
                grid_portion = round((grid / used) * 100, 2) if used > 0 else 0.0

                latest_data = {
                    "hour": hour.isoformat(),
                    "community_depleted": depleted,
                    "grid_portion": grid_portion
                }
            else:
                latest_data = {}
        except Exception as e:
            print("[Percentage-Service] Error:", e)
            print("[Percentage-Service] Will retry in 5 seconds...")
        stop_event.wait(5)  # Update every 5 seconds

# delivers the newest percentages: how much energy was taken from the network vs community 
@app.route('/percentage')
def percentage():
    if latest_data:
        return jsonify(latest_data)
    return jsonify({"error": "No data available"}), 404

@app.route('/start')
def start_percentage_service():
    global percentage_thread
    if percentage_thread is None or not percentage_thread.is_alive():
        stop_event.clear()
        percentage_thread = threading.Thread(target=update_percentage_loop, daemon=True)
        percentage_thread.start()
        return "Percentage service started.\n"
    return "Percentage service already running.\n"

@app.route('/stop')
def stop_percentage_service():
    stop_event.set()
    return "Percentage service stopping...\n"

if __name__ == '__main__':
    stop_event.clear()
    percentage_thread = threading.Thread(target=update_percentage_loop, daemon=True)
    percentage_thread.start()
    app.run(host='0.0.0.0', port=5008)
