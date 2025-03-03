from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Add this
import csv
import os

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

BCRM_FILE = "bcrm.csv"
USED_FILE = "used_meters.csv"
NOT_IN_BCRM_FILE = "not_in_bcrm.csv"

# Load BCRM meter numbers
def load_bcrm_meters():
    if not os.path.exists(BCRM_FILE):
        return set()
    with open(BCRM_FILE, "r") as f:
        return set(row[0] for row in csv.reader(f))

# Check if meter exists in BCRM
@app.route("/check_meter", methods=["GET"])
def check_meter():
    meter_number = request.args.get("meter_number")
    bcrm_meters = load_bcrm_meters()
    
    if meter_number in bcrm_meters:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})

# Register a used meter
@app.route("/register_meter", methods=["POST"])
def register_meter():
    data = request.json
    meter_number = data.get("meter_number")

    bcrm_meters = load_bcrm_meters()
    
    if meter_number in bcrm_meters:
        file_path = USED_FILE
    else:
        file_path = NOT_IN_BCRM_FILE

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([meter_number])

    return jsonify({"status": "success", "message": "Meter registered."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)  # ✅ Make sure it's accessible on Render
