## @file daily_upload.py
#  @brief Reads local weather data, uploads temperatures to ThingsBoard, and appends them to a historical dataset.
#  @details
#  This script performs the following:
#  - Reads today's recorded weather CSV file.
#  - Extracts max and min temperatures.
#  - Sends them to ThingsBoard via its API.
#  - Appends the values to a historical file (`bostonweather.csv`) if not already present.

import os
import pandas as pd
import requests
from datetime import datetime

## @var ACCESS_TOKEN
#  @brief Access token for ThingsBoard Cloud API.
#  @note Must change this because it will be different when setting up your ThingsBoard
ACCESS_TOKEN = "ivcoixXiUzBWe0zdNtjv"

## @var current_dir
# @brief Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))

## @var project_root
# @brief Project root is assumed to be two levels above this script
project_root = os.path.dirname(os.path.dirname(current_dir))

## @var localWeatherFolder
#  @brief Path to folder containing daily local weather CSV files.
localWeatherFolder = os.path.join(project_root, "weather_analysis", "data", "localweather")

## @var bostonweather_path
#  @brief Path to historical weather CSV file (bostonweather.csv).
bostonweather_path = os.path.join(os.path.dirname(os.getcwd()), "data", "bostonweather.csv")

## @brief Reads today's weather CSV and extracts max and min temperature.
#  @return tuple: (max_temp, min_temp) as floats, or (None, None) if file is missing or unreadable.
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

## @brief Sends the maximum and minimum temperatures to ThingsBoard.
#  @param max_temp (float) The maximum temperature of the day.
#  @param min_temp (float) The minimum temperature of the day.
#  @details Sends data via a POST request to the ThingsBoard telemetry endpoint.
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
        print(f" Error sending to ThingsBoard: {e}")

## @brief Appends today's max and min temperatures to bostonweather.csv.
#  @param max_temp (float): The maximum temperature of the day.
#  @param min_temp (float): The minimum temperature of the day.
#  @details Makes a new row in bostonweather.csv and appends today's data.
#  Also ensures that today's entry is not duplicated before appending.
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


## @brief Main function to orchestrate reading, sending, and appending today's max and min temperatures.
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
