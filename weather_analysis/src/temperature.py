import os
import re
import serial
import csv
import subprocess
import platform
from datetime import datetime
from wifi import Cell, Scheme

# Get the current working directory, then go up to project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

esp32_sketch_path = os.path.join(project_root, "weather_station")  # Folder containing your .ino file
esp32_board = "esp32:esp32:esp32wroverkit"  # Replace if you're using another ESP32 variant
esp32_port = "COM3"  # Adjust as needed if COM is different
localWeatherFolder = os.path.join(project_root, "weather_analysis", "data",
                                  "localweather")  # Folder to contain recorded weather data.


def list_ssid():
    os_name = platform.system()
    ssids = []

    try:
        if os_name == "Windows":
            output = subprocess.check_output('netsh wlan show networks', shell=True, text=True)
            # Extract SSIDs using regex (skip "SSID N : " format)
            ssids = re.findall(r'\s+SSID\s+\d+\s+:\s(.+)', output)

        elif os_name == "Linux":
            output = subprocess.check_output("nmcli device wifi list", shell=True, text=True)
            # Extract SSID names from each line (ignoring the header)
            lines = output.strip().split('\n')[1:]
            for line in lines:
                parts = line.strip().split()
                if parts:
                    ssids.append(parts[0])

        else:
            print("Unsupported OS")
    except subprocess.CalledProcessError as e:
        print(f"Error listing networks: {e}")

    return ssids


def get_current_ssid():
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
        ssid_match = re.search(r'\s+SSID\s+:\s(.+)', output)
        if ssid_match:
            return ssid_match.group(1).strip()
    except subprocess.CalledProcessError:
        pass
    return None


# Automatically updates the password in the ino file based on user input.
def update_wifi_password_in_ino(ssid, password):
    # Creates a variable for the ino files and its path.
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    # Open the ino files to be read.
    with open(ino_path, 'r') as file:
        code = file.read()

    # Perform both substitutions on the full content
    updated_code = re.sub(r'const char\* ssid = ".*?";', f'const char* ssid = "{ssid}";', code)
    updated_code = re.sub(r'const char\* password = ".*?";', f'const char* password = "{password}";', updated_code)

    with open(ino_path, 'w') as file:
        file.write(updated_code)

    print(f"✅ Wi-Fi ssid and password updated in {ino_file}")


# Function to reset ssid and password of user once the program ends.
def clear_wifi_credentials():
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    with open(ino_path, 'r') as file:
        code = file.read()

    cleared_code = re.sub(r'const char\* ssid = ".*?";', 'const char* ssid = "SSID";', code)
    cleared_code = re.sub(r'const char\* password = ".*?";', 'const char* password = "PASSWORD";', cleared_code)

    with open(ino_path, 'w') as file:
        file.write(cleared_code)

    print("🧹 Wi-Fi credentials cleared from .ino file.")


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
            clear_wifi_credentials()


def _main():
    ssid = get_current_ssid()
    if not ssid:
        print("❌ Could not detect SSID automatically.")
        available_ssids = list_ssid()

        if not available_ssids:
            print("❌ No networks found.")
            return

        print("\n📡 Available Networks:")
        for i, network in enumerate(available_ssids, start=1):
            print(f"{i}. {network}")

        while True:
            try:
                choice = int(input("Select the number of the network you want to connect to: "))
                if 1 <= choice <= len(available_ssids):
                    ssid = available_ssids[choice - 1]
                    break
                else:
                    print("⚠️ Invalid selection. Please choose a valid number.")
            except ValueError:
                print("⚠️ Please enter a number.")
    else:
        print(f"📶 Detected network: {ssid}")

    wifi_password = input("🔐 Enter your Wi-Fi password: ")
    update_wifi_password_in_ino(ssid, wifi_password)
    compile_and_upload()
    gatherLocalWeather()


if __name__ == '__main__':
    _main()
