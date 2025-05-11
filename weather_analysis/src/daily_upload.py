import os
import pandas as pd
import requests
from datetime import datetime

# Config
ACCESS_TOKEN = "ivcoixXiUzBWe0zdNtjv"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
localWeatherFolder = os.path.join(project_root, "weather_analysis", "data",
                                  "localweather")  # Folder to contain recorded weather data.

bostonweather_path = os.path.join(os.path.dirname(os.getcwd()), "data", "bostonweather.csv")


def get_max_min_temperature_from_today():
    today = datetime.now().strftime("%d-%m-%Y")
    today_csv_path = os.path.join(localWeatherFolder, f"{today}.csv")

    if not os.path.exists(today_csv_path):
        print(f"No data file for today: {today_csv_path}")
        return None, None

    try:
        df = pd.read_csv(today_csv_path, encoding_errors='ignore')
        df['Temp (F)'] = pd.to_numeric(df['Temp (F)'], errors='coerce')
        max_temp = df['Temp (F)'].max()
        min_temp = df['Temp (F)'].min()
        return max_temp, min_temp
    except Exception as e:
        print(f"Error reading today's CSV: {e}")
        return None, None


def send_daily_temps_to_thingsboard(max_temp, min_temp):
    url = f"https://thingsboard.cloud/api/v1/{ACCESS_TOKEN}/telemetry"
    payload = {
        "tmax": round(max_temp, 2),
        "tmin": round(min_temp, 2)
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Successfully sent tmax and tmin to ThingsBoard")
        else:
            print(f"Failed to send data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error sending to ThingsBoard: {e}")


def append_today_to_bostonweather(max_temp, min_temp):
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(bostonweather_path):
        df = pd.read_csv(bostonweather_path)

        if today not in df['DATE'].values:
            new_row = {
                "DATE": today,
                "PRCP": 0,
                "SNOW": 0,
                "SNWD": 0,
                "TMAX": max_temp,
                "TMIN": min_temp,
                "AWND": 0
            }
            df = df._append(new_row, ignore_index=True)
            df.to_csv(bostonweather_path, index=False)
            print(f"Appended today's data to bostonweather.csv.")
        else:
            print("Today's data already exists. Skipping.")
    else:
        print(f" Bostonweather.csv not found at {bostonweather_path}")


def main():
    max_temp, min_temp = get_max_min_temperature_from_today()

    if max_temp is not None and min_temp is not None:
        print(f"Today's Tmax: {max_temp:.2f} °F, Tmin: {min_temp:.2f} °F")

        send_daily_temps_to_thingsboard(max_temp, min_temp)
        append_today_to_bostonweather(max_temp, min_temp)
    else:
        print("No data to upload.")


if __name__ == "__main__":
    main()
