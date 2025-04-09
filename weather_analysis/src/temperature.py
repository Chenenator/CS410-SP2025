import os
import serial
import csv
from datetime import datetime

# Create filename with current day, month, and year
date_str = datetime.now().strftime("%d-%m-%Y")
folder = "C:/Users/denni/PycharmProjects/weather_analysis/data/localweather"
os.makedirs(folder, exist_ok=True)  # Ensure folder exists
filename = os.path.join(folder, f"{date_str}.csv")

port = 'COM3'
baud = 9600

ser = serial.Serial(port, baud, timeout=1)

# Check if file already exists
file_exists = os.path.isfile(filename)

with open(filename, mode='a', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Only write header if file didn't exist
    if not file_exists:
        writer.writerow(['Timestamp', 'Humidity (%)', 'Temp (°C)', 'Temp (°F)'])

    print("Listening to ESP32 serial output... Press Ctrl+C to stop.")

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"ESP32: {line}")
                parts = line.split(',')
                if len(parts) == 3:
                    timestamp = datetime.now().isoformat(timespec='seconds')
                    humi = parts[0].strip()
                    tempC = parts[1].strip()
                    tempF = parts[2].strip()
                    writer.writerow([timestamp, humi, tempC, tempF])
                    csv_file.flush()
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        ser.close()
