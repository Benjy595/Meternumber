from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

BCRM_FILE = "bcrm.csv"
USED_METERS_FILE = "used_meters.csv"

# Ensure used meters file exists with a header
if not os.path.exists(USED_METERS_FILE):
    with open(USED_METERS_FILE, "w") as f:
        f.write("meter_number,in_bcrm\n")

def load_bcrm_meters():
    """Load meter numbers along with latitude & longitude from bcrm.csv"""
    meters = {}
    try:
        with open(BCRM_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "meter_number" in row and "latitude" in row and "longitude" in row:
                    meters[row["meter_number"].strip()] = (row["latitude"].strip(), row["longitude"].strip())
    except Exception as e:
        print(f"Error reading {BCRM_FILE}: {e}")
    print("Loaded meters:", meters)  # Debugging print
    return meters

@app.route("/check_meter", methods=["GET"])
def check_meter():
    meter_number = request.args.get("meter_number", "").strip()
    
    if not meter_number:
        return jsonify({"error": "No meter number provided"}), 400
    
    meters = load_bcrm_meters()
    
    if meter_number in meters:
        lat, lon = meters[meter_number]
        return jsonify({"exists": True, "latitude": lat, "longitude": lon})
    
    return jsonify({"exists": False})

@app.route("/register_meter", methods=["POST"])
def register_meter():
    data = request.json
    meter_number = data.get("meter_number", "").strip()

    if not meter_number:
        return jsonify({"error": "No meter number provided"}), 400
    
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
