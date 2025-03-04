import sqlite3
import csv

DB_FILE = "meters.db"  # SQLite database file
CSV_FILE = "bcrm.csv"  # Your CSV file

# Connect to SQLite (creates the file if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create table (modify column names if needed)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bcrm_meters (
        meter_number TEXT PRIMARY KEY
    )
""")

# Read CSV and insert data into SQLite
with open(CSV_FILE, "r", newline="") as file:
    reader = csv.reader(file)
    next(reader, None)  # Skip header if exists
    for row in reader:
        try:
            cursor.execute("INSERT INTO bcrm_meters (meter_number) VALUES (?)", (row[0],))
        except sqlite3.IntegrityError:
            pass  # Ignore duplicates

conn.commit()
conn.close()

print("CSV data imported into SQLite successfully!")
