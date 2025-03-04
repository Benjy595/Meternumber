from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_FILE = "meters.db"  # ✅ SQLite database file

# ✅ Initialize the database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meter_number TEXT UNIQUE NOT NULL,
                exists_in_bcrm BOOLEAN NOT NULL
            )
        """)
        conn.commit()

init_db()  # ✅ Create table if it doesn't exist

# ✅ Check if meter exists in the database
@app.route("/check_meter", methods=["GET"])
def check_meter():
    meter_number = request.args.get("meter_number")
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT exists_in_bcrm FROM meters WHERE meter_number = ?", (meter_number,))
        row = cur.fetchone()

    return jsonify({"exists": bool(row[0]) if row else False})

# ✅ Register a new meter number
@app.route("/register_meter", methods=["POST"])
def register_meter():
    data = request.json
    meter_number = data.get("meter_number")
    exists_in_bcrm = data.get("exists_in_bcrm", False)  # Default: Not in BCRM

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO meters (meter_number, exists_in_bcrm) VALUES (?, ?)", 
                        (meter_number, exists_in_bcrm))
            conn.commit()
            return jsonify({"status": "success", "message": "Meter registered."})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Meter already registered!"}), 400

# ✅ Get all registered meters (for download)
@app.route("/download_meters", methods=["GET"])
def download_meters():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT meter_number, exists_in_bcrm FROM meters")
        meters = cur.fetchall()

    csv_data = "Meter Number,Exists in BCRM\n"
    csv_data += "\n".join([f"{m[0]},{'Yes' if m[1] else 'No'}" for m in meters])

    return csv_data, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=meters.csv"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
