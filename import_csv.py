import sqlite3
import csv

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("meters.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bcrm_meters (
        meter_number TEXT PRIMARY KEY
    )
""")

# Open and read CSV file
with open("bcrm.csv", "r", newline="", encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)  # Skip header if CSV has one

    for row in csv_reader:
        meter_number = row[0].strip()  # Adjust if meter number is in a different column
        cursor.execute("INSERT OR IGNORE INTO bcrm_meters (meter_number) VALUES (?)", (meter_number,))

# Commit and close connection
conn.commit()
conn.close()

print("CSV data imported successfully!")
