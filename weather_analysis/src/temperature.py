import os
import re
import serial
import csv
import subprocess
from datetime import datetime

# CONFIGURATION
esp32_sketch_path = ("C:/Users/denni/OneDrive - University of Massachusetts Boston/Documents/CS410 "
                     "Materials/CS410-SP2025/weather_station")  # Folder containing your .ino file
esp32_board = "esp32:esp32:esp32wroverkit"  # Replace if you're using another ESP32 variant
esp32_port = "COM3"  # Adjust as needed
localWeatherFolder = ("C:/Users/denni/OneDrive - University of Massachusetts Boston/Documents/CS410 "
                      "Materials/CS410-SP2025/weather_analysis/data/localweather")


def update_wifi_password_in_ino(ssid, password):
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    with open(ino_path, 'r') as file:
        code = file.read()

    # Perform both substitutions on the full content
    updated_code = re.sub(r'const char\* ssid = ".*?";', f'const char* ssid = "{ssid}";', code)
    updated_code = re.sub(r'const char\* password = ".*?";', f'const char* password = "{password}";', updated_code)

    with open(ino_path, 'w') as file:
        file.write(updated_code)

    print(f"✅ Wi-Fi ssid and password updated in {ino_file}")


def compile_and_upload():
    print("🔧 Compiling sketch...")
    compile_cmd = ["arduino-cli", "compile", "--fqbn", esp32_board, esp32_sketch_path]
    subprocess.run(compile_cmd, check=True)

    print("📤 Uploading to ESP32...")
    upload_cmd = ["arduino-cli", "upload", "-p", esp32_port, "--fqbn", esp32_board, esp32_sketch_path]
    subprocess.run(upload_cmd, check=True)

    print("✅ Upload complete!")


def gatherLocalWeather():
    date_str = datetime.now().strftime("%d-%m-%Y")
    os.makedirs(localWeatherFolder, exist_ok=True)
    filename = os.path.join(localWeatherFolder, f"{date_str}.csv")

    ser = serial.Serial(esp32_port, 9600, timeout=1)
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Humidity (%)', 'Temp (°C)', 'Temp (°F)'])

        print("📡 Listening to ESP32 serial output... Press Ctrl+C to stop.")
        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"ESP32: {line}")
                    parts = line.split(',')
                    if len(parts) == 3:
                        timestamp = datetime.now().isoformat(timespec='seconds')
                        writer.writerow([timestamp, *[p.strip() for p in parts]])
                        csv_file.flush()
        except KeyboardInterrupt:
            print("🛑 Data logging stopped.")
        finally:
            ser.close()


def _main():
    ssid = input("Enter SSID: ")
    wifi_password = input("🔐 Enter your Wi-Fi password: ")
    update_wifi_password_in_ino(ssid, wifi_password)
    compile_and_upload()
    gatherLocalWeather()


if __name__ == '__main__':
    _main()
