from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import csv

app = Flask(__name__)
CORS(app)

DB_FILE = "meters.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bcrm_meters (
                meter_number TEXT PRIMARY KEY
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS used_meters (
                meter_number TEXT PRIMARY KEY,
                in_bcrm BOOLEAN
            )
        """)
        conn.commit()

@app.route("/check_meter", methods=["GET"])
def check_meter():
    meter_number = request.args.get("meter_number")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM bcrm_meters WHERE meter_number = ?", (meter_number,))
        exists = cursor.fetchone() is not None
    return jsonify({"exists": exists})

@app.route("/register_meter", methods=["POST"])
def register_meter():
    data = request.json
    meter_number = data.get("meter_number")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM bcrm_meters WHERE meter_number = ?", (meter_number,))
        in_bcrm = cursor.fetchone() is not None

        # Avoid duplicate registrations
        cursor.execute("INSERT OR IGNORE INTO used_meters (meter_number, in_bcrm) VALUES (?, ?)", (meter_number, in_bcrm))
        conn.commit()

    return jsonify({"status": "success", "message": "Meter registered."})

@app.route("/download_meters", methods=["GET"])
def download_meters():
    csv_path = "used_meters.csv"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT meter_number, in_bcrm FROM used_meters")
        rows = cursor.fetchall()

    # Ensure proper CSV formatting
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Meter Number", "In BCRM"])
        writer.writerows(rows)

    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000, debug=True)
