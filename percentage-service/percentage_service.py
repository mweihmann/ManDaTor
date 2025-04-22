from flask import Flask, jsonify
import psycopg2
from datetime import datetime
from database.util.db import get_connection

app = Flask(__name__)

# delivers the newest percentages: how much energy was taken from the network vs community 
@app.route('/percentage')
def percentage():
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
        return jsonify({
            "hour": hour.isoformat(),
            "community_depleted": depleted,
            "grid_portion": grid_portion
        })
    return jsonify({"error": "No data available"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
