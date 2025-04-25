import os
import re
import requests
import serial
import csv
import subprocess
import platform
from datetime import datetime
import pyautogui
<<<<<<< Updated upstream
import pandas as pd
=======
import json
>>>>>>> Stashed changes

# Get the current working directory, then go up to project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

esp32_sketch_path = os.path.join(project_root, "weather_station")  # Folder containing your .ino file
esp32_board = "esp32:esp32:esp32wroverkit"  # Replace if you're using another ESP32 variant
esp32_port = "COM3"  # Adjust as needed if COM is different
localWeatherFolder = os.path.join(project_root, "weather_analysis", "data",
                                  "localweather")  # Folder to contain recorded weather data.


# For when the program cannot detect the current network, list them out
# for the user to choose.
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


# Get the current network credentials.
def get_current_network_credentials(ssid):
    try:
        # Get current connected SSID
        current_output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
        ssid_match = re.search(r'\s*SSID\s*:\s(.+)', current_output)
        if not ssid_match:
            print("Could not find SSID.")
            return

        current_ssid = ssid_match.group(1).strip()
        print(f"Current SSID: {current_ssid}")

        # If the parameter is not empty, indicating that the current ssid could not be found,
        # find the password of the manually inputted ssid.
        if ssid is not None:
            # Show profile details with key=clear
            profile_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'],
                                                     encoding='utf-8')
        else:
            # Show profile details with key=clear
            profile_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', current_ssid, 'key=clear'],
                                                     encoding='utf-8')

        # Obtain password of matching ssid.
        key_match = re.search(r'Key Content\s*:\s(.+)', profile_output)

        if key_match:
            print(f"Password: {key_match.group(1).strip()}")
            return current_ssid, key_match.group(1).strip()
        else:
            print("Password not found. Either on Eduroam or Open Network.")
            return current_ssid, None

    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")


# Automatically updates the password in the ino file based on user input.
def update_wifi_credentials_in_ino(ssid, password):
    # Creates a variable for the ino files and its path.
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    # Open the ino files to be read.
    with open(ino_path, 'r') as file:
        code = file.read()

    # Error checking to make sure fields are in .ino file.
    if 'const char* ssid =' not in code or 'const char* password =' not in code:
        print("⚠️ Could not locate ssid/password fields. Make sure the .ino file has the expected format.")
        return

    # In the .ino file, change the ssid and password fields of current connected network.
    updated_code = re.sub(r'const char\* ssid = ".*?";', f'const char* ssid = "{ssid}";', code)
    updated_code = re.sub(r'const char\* password = ".*?";', f'const char* password = "{password}";', updated_code)

    # Write to file.
    with open(ino_path, 'w') as file:
        file.write(updated_code)

    print(f"✅ Wi-Fi ssid and password updated in {ino_file}")


def update_wifi_credentials_eduroam_in_ino(ssid, password, eduroam_username, eduroam_identity):
    # Creates a variable for the ino files and its path.
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    # Open the ino files to be read.
    with open(ino_path, 'r') as file:
        code = file.read()

    # Error checking to make sure fields are in .ino file.
    if 'const char* ssid =' not in code or 'const char* password =' not in code or "const char* eduroam_username" not in code or "const char* eduroam_identity" not in code:
        print("⚠️ Could not locate ssid/password fields. Make sure the .ino file has the expected format.")
        return

    # Update fields ssid, password, eduroam_username, and eduroam_identity.
    updated_code = re.sub(r'const char\* ssid = ".*?";', f'const char* ssid = "{ssid}";', code)
    updated_code = re.sub(r'const char\* password = ".*?";', f'const char* password = "{password}";', updated_code)
    updated_code = re.sub(r'const char\* eduroam_username = ".*?";',
                          f'const char* eduroam_username = "{eduroam_username}";', updated_code)
    updated_code = re.sub(r'const char\* eduroam_identity = ".*?";',
                          f'const char* eduroam_identity = "{eduroam_identity}";', updated_code)

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
    cleared_code = re.sub(r'const char\* eduroam_username = ".*?";',
                          'const char* eduroam_username = "UNIVERSITY_EMAIL";', cleared_code)
    cleared_code = re.sub(r'const char\* eduroam_identity = ".*?";',
                          'const char* eduroam_identity = "UNIVERSITY_EMAIL";', cleared_code)

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


# Obtain the local weather data recorded and puts it into csv file.
def gather_local_weather():
    date_str = datetime.now().strftime("%Y-%m-%d")
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

def get_max_min_temperature_from_csv(csv_path):
    """
    Reads a CSV file generated by ESP32 and returns the max and min temperatures (in F).
    Assumes the CSV has a column 'Temp (°C)'.
    """
    try:
        df = pd.read_csv(csv_path)
        max_temp = df['Temp (°F)'].max()
        min_temp = df['Temp (°F)'].min()
        return max_temp, min_temp
    except Exception as e:
        print(f"Error reading temperature from file: {e}")
        return None, None

def send_daily_temps_to_thingsboard(max_temp, min_temp, access_token):
    url = f"https://thingsboard.cloud/api/v1/{access_token}/telemetry"
    payload = {
        "tmax": round(max_temp, 2),
        "tmin": round(min_temp, 2)
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Successfully sent tmax and tmin to ThingsBoard")
        else:
            print(f"❌ Failed to send data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error while sending to ThingsBoard: {e}")


def _main():
    clear_wifi_credentials()
    ssid, wifi_password = get_current_network_credentials(None)
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
                    _, wifi_password = get_current_network_credentials(ssid)
                    break
                else:
                    print("⚠️ Invalid selection. Please choose a valid number.")
            except ValueError:
                print("⚠️ Please enter a number.")
    else:
        print(f"📶 Detected network: {ssid}")

    if "eduroam" in ssid.lower():
        eduroam_credential = input("Enter your University Email address: ")
        eduroam_password = pyautogui.password(text='', title='', default='', mask='*')
        update_wifi_credentials_eduroam_in_ino(ssid, eduroam_password, eduroam_credential, eduroam_credential)
        compile_and_upload()
        gather_local_weather()
    else:
        update_wifi_credentials_in_ino(ssid, wifi_password)
        compile_and_upload()
        gather_local_weather()

    latest_file = sorted(os.listdir(localWeatherFolder))[-1]
    latest_path = os.path.join(localWeatherFolder, latest_file)
    max_temp, min_temp = get_max_min_temperature_from_csv(latest_path)

    if max_temp is not None and min_temp is not None:
        print(f"\n📊 Max Temp: {max_temp:.2f} °F")
        print(f"📊 Min Temp: {min_temp:.2f} °F")

        # Replace this with your actual device token
        THINGSBOARD_TOKEN = "ivcoixXiUzBWe0zdNtjv"
        send_daily_temps_to_thingsboard(max_temp, min_temp, THINGSBOARD_TOKEN)

if __name__ == '__main__':
    _main()
