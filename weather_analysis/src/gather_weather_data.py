import requests
import time
import csv
from datetime import datetime

# --------------- Configuration -----------------

THINGSBOARD_URL = "https://thingsboard.cloud"
USERNAME = "dennis.wong002@umb.edu"  # <-- your ThingsBoard login
PASSWORD = 123456  # <-- your ThingsBoard password
DEVICE_ID = "8b534c60-1667-11f0-8f83-43727cd6bc90"  # <-- your deviceId (UUID)

FETCH_INTERVAL = 300  # Fetch every 300 seconds (5 minutes)
TOKEN_REFRESH_INTERVAL = 3000  # Refresh login every 50 minutes
DATA_KEYS = "TempF,Humidity"
CSV_FILENAME = datetime.now().strftime("%d-%m-%Y") + ".csv"

# ------------------------------------------------

session = requests.Session()
jwt_token = None
token_last_refresh_time = None


def login():
    global jwt_token, token_last_refresh_time
    login_url = f"{THINGSBOARD_URL}/api/auth/login"
    credentials = {"username": USERNAME, "password": PASSWORD}

    response = session.post(login_url, json=credentials)

    if response.status_code == 200:
        jwt_token = response.json().get("token")
        token_last_refresh_time = time.time()
        print(f"[{datetime.now()}] ✅ Logged in successfully.")
    else:
        print(f"[{datetime.now()}] ❌ Failed to login. {response.text}")
        raise Exception("Login failed!")


def fetch_telemetry():
    telemetry_url = f"{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries?keys={DATA_KEYS}"
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    response = session.get(telemetry_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"[{datetime.now()}] ❌ Failed to fetch telemetry. {response.status_code}")
        print(response.text)
        return None


def save_to_csv(data):
    # Prepare the row
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp = data.get("TempF", [{}])[0].get("value", "N/A")
    humidity = data.get("Humidity", [{}])[0].get("value", "N/A")

    row = [timestamp, temp, humidity]

    # Create CSV file if doesn't exist
    try:
        with open(CSV_FILENAME, "x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Temperature (°F)", "Humidity (%)"])
    except FileExistsError:
        pass  # Already exists

    # Append new data
    with open(CSV_FILENAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

    print(f"[{datetime.now()}] 📥 Saved: Temp={temp}°F, Humidity={humidity}%")


# ----------------- Main Loop -------------------

if __name__ == "__main__":
    try:
        login()

        while True:
            # Refresh token if needed
            if time.time() - token_last_refresh_time > TOKEN_REFRESH_INTERVAL:
                print(f"[{datetime.now()}] 🔄 Refreshing JWT token...")
                login()

            # Fetch telemetry
            data = fetch_telemetry()
            if data:
                save_to_csv(data)

            # Wait before next fetch
            time.sleep(FETCH_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
