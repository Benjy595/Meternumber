from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

BCRM_FILE = "bcrm.csv"
USED_METERS_FILE = "used_meters.csv"

# Ensure used meters file exists
if not os.path.exists(USED_METERS_FILE):
    with open(USED_METERS_FILE, "w") as f:
        f.write("meter_number,in_bcrm\n")  # CSV header

def load_bcrm_meters():
    """Load all meter numbers from bcrm.csv"""
    with open(BCRM_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return {row[0] for row in reader}  # Store as a set for fast lookup

@app.route("/check_meter", methods=["GET"])
def check_meter():
    meter_number = request.args.get("meter_number")
    meters = load_bcrm_meters()
    return jsonify({"exists": meter_number in meters})

@app.route("/register_meter", methods=["POST"])
def register_meter():
    data = request.json
    meter_number = data.get("meter_number")
    meters = load_bcrm_meters()
    in_bcrm = meter_number in meters

    # Append to used_meters.csv
    with open(USED_METERS_FILE, "a") as f:
        f.write(f"{meter_number},{in_bcrm}\n")

    return jsonify({"status": "success", "message": "Meter registered."})

@app.route("/download_meters", methods=["GET"])
def download_meters():
    return send_file(USED_METERS_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
