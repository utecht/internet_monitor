import requests
import sqlite3
import schedule
import time
from datetime import datetime

# Define the URL to check
TEST_URL = "https://www.google.com"
DB_PATH = "/data/internet_status.db"

# Connect to (or create) the SQLite database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create a table to store outage data
c.execute("""
    CREATE TABLE IF NOT EXISTS outages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        end_time TEXT,
        duration REAL
    )
""")
conn.commit()

# Variables to track outage state
outage_in_progress = False
outage_start_time = None


def check_internet():
    global outage_in_progress, outage_start_time
    try:
        # Try to make a GET request to the test URL
        response = requests.get(TEST_URL, timeout=5)
        if response.status_code == 200:
            if outage_in_progress:
                # Internet has come back after an outage
                outage_in_progress = False
                outage_end_time = datetime.now()
                duration = (outage_end_time - outage_start_time).total_seconds()
                # Log the outage to the database
                c.execute(
                    """
                    INSERT INTO outages (start_time, end_time, duration)
                    VALUES (?, ?, ?)
                """,
                    (
                        outage_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        outage_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        duration,
                    ),
                )
                conn.commit()
                print(
                    f"Outage ended at {outage_end_time}, duration: {duration} seconds"
                )
        else:
            # Non-200 status code, treat as outage
            start_outage()
    except requests.RequestException:
        # Exception occurred, likely no internet
        start_outage()


def start_outage():
    global outage_in_progress, outage_start_time
    if not outage_in_progress:
        outage_in_progress = True
        outage_start_time = datetime.now()
        print(f"Outage started at {outage_start_time}")


# Schedule the check every minute
schedule.every(1).minutes.do(check_internet)

print("Starting internet monitoring...")
while True:
    schedule.run_pending()
    time.sleep(1)
