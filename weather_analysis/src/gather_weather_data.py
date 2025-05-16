## @file gather_weather_data.py
#  @brief Periodically fetches and logs telemetry data from ThingsBoard.
#  @details
#  This script authenticates with the ThingsBoard Cloud API using JWT,
#  retrieves telemetry values (temperature and humidity), and appends
#  them to a daily CSV log. It supports automatic token refresh and
#  runs as a continuous loop at defined intervals.

import requests
import time
import csv
from datetime import datetime

# --------------- Configuration -----------------
## @var THINGSBOARD_URL
#  @brief Base URL of the ThingsBoard Cloud instance.
THINGSBOARD_URL = "https://thingsboard.cloud"

## @var USERNAME
#  @brief Username/email for logging into ThingsBoard.
#  @note  Change this to match your account
USERNAME = "dennis.wong002@umb.edu"

## @var PASSWORD
#  @brief Password for ThingsBoard account.
#  @note Change this to match your account
PASSWORD = 123456  # <-- your ThingsBoard password

## @var DEVICE_ID
#  @brief The UUID of the device from which telemetry is fetched.
#  @note Change this to match your device ID (UUID)
DEVICE_ID = "8b534c60-1667-11f0-8f83-43727cd6bc90"

## @var FETCH_INTERVAL
#  @brief Number of seconds between each telemetry fetch (default: 300s = 5min).
FETCH_INTERVAL = 300
## @var TOKEN_REFRESH_INTERVAL
#  @brief Time in seconds to refresh the JWT token (default: 3000s = 50min).
TOKEN_REFRESH_INTERVAL = 3000

## @var DATA_KEYS
#  @brief Comma-separated telemetry keys to fetch from ThingsBoard.
DATA_KEYS = "TempF,Humidity"

## @var CSV_FILENAME
#  @brief Filename to store telemetry data for the current day.
CSV_FILENAME = datetime.now().strftime("%d-%m-%Y") + ".csv"

# ------------------------------------------------
## @var session
#  @brief A reusable requests session object.
session = requests.Session()
## @var jwt_token
#  @brief Stores the JWT access token after login.
jwt_token = None
## @var token_last_refresh_time
#  @brief Timestamp of the last token refresh.
token_last_refresh_time = None

## @brief Logs into ThingsBoard and retrieves a JWT token.
#  @throws Error if login fails.
#  @details Sends credentials to the ThingsBoard login API and stores the received token.
def login():
    global jwt_token, token_last_refresh_time
    login_url = f"{THINGSBOARD_URL}/api/auth/login"
    credentials = {"username": USERNAME, "password": PASSWORD}

    response = session.post(login_url, json=credentials)

    if response.status_code == 200:
        jwt_token = response.json().get("token")
        token_last_refresh_time = time.time()
        print(f"[{datetime.now()}] Logged in successfully.")
    else:
        print(f"[{datetime.now()}] Failed to login. {response.text}")
        raise Exception("Login failed!")

## @brief Fetches telemetry data from ThingsBoard for specified keys.
#  @return dict: JSON dictionary of telemetry data, or None on failure.
#  @details Sends a GET request using the current JWT token to fetch telemetry values.
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
        print(f"[{datetime.now()}] Failed to fetch telemetry. {response.status_code}")
        print(response.text)
        return None

## @brief Saves telemetry data (temperature and humidity) to a daily CSV file.
#  @param data: The telemetry dictionary returned from fetch_telemetry().
#  @details Appends a timestamped row of telemetry data to the log CSV. Creates header if the file does not exist.
def save_to_csv(data):

    # Prepare the row
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp = data.get("TempF", [{}])[0].get("value", "N/A")
    humidity = data.get("Humidity", [{}])[0].get("value", "N/A")

    row = [timestamp, temp, humidity]

    # Create CSV file if it doesn't exist
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

    print(f"[{datetime.now()}] Saved: Temp={temp}°F, Humidity={humidity}%")


# ----------------- Main Loop -------------------

## @brief Main execution loop to log data continuously.
#  @details Handles login, periodic telemetry fetch, token refresh, and data logging.
if __name__ == "__main__":
    try:
        login()

        while True:
            # Refresh token if needed
            if time.time() - token_last_refresh_time > TOKEN_REFRESH_INTERVAL:
                print(f"[{datetime.now()}] Refreshing JWT token...")
                login()

            # Fetch telemetry
            data = fetch_telemetry()
            if data:
                save_to_csv(data)

            # Wait before next fetch
            time.sleep(FETCH_INTERVAL)

    except KeyboardInterrupt:
        print("\n Program stopped by user.")
    except Exception as e:
        print(f"\n Error: {str(e)}")
