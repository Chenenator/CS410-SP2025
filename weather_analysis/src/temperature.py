## @file temperature.py
#  @brief Automates ESP32 Wi-Fi setup, sketch upload, and serial weather data logging.
#  @details This script:
#  - Detects or prompts for a Wi-Fi network (supports Eduroam).
#  - Injects credentials into an Arduino sketch.
#  - Compiles and uploads the sketch via arduino-cli.
#  - Reads sensor data from the ESP32 over serial.
#  - Logs readings to a daily CSV file.

import os
import re
import serial
import csv
import subprocess
import platform
from datetime import datetime
import pyautogui

## @var current_dir
#  @brief Directory of this script file.
current_dir = os.path.dirname(os.path.abspath(__file__))
## @var project_root
#  @brief Root of the project directory.
project_root = os.path.dirname(os.path.dirname(current_dir))

## @var esp32_sketch_path
#  @brief Path to folder containing the ESP32 Arduino sketch (.ino file).
#  @note change "weather_station" if your .ino file is different
esp32_sketch_path = os.path.join(project_root, "weather_station")

## @var esp32_board
#  @brief Board type for arduino-cli to compile for.
#  @note Replace "esp32:esp32:esp32wroverkit" if you're using another ESP32 variant
esp32_board = "esp32:esp32:esp32wroverkit"

## @var esp32_port
#  @brief Serial port for ESP32 device.
#  @note  Adjust as needed if COM port is different
esp32_port = "COM3"

## @var localWeatherFolder
#  @brief Path where local weather CSV logs are stored.
localWeatherFolder = os.path.join(project_root, "weather_analysis", "data",
                                  "localweather")

## @brief Lists nearby Wi-Fi SSIDs using system commands.
#  @return List of detected SSID names.
#  @details Uses `netsh` on Windows and `nmcli` on Linux to scan for visible Wi-Fi networks.
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


## @brief Retrieves the password of the current or specified SSID from Windows profiles.
#  @param ssid Optional. SSID to look up manually. If None, uses the currently connected network.
#  @return Tuple: (SSID, Password) or (SSID, None) if not found.
#  @details Uses `netsh wlan show profile` to get the saved credentials from the system.
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


## @brief Updates the SSID and password fields in the Arduino sketch.
#  @param ssid Wi-Fi SSID.
#  @param password Wi-Fi password.
#  @details Modifies the `const char* ssid` and `password` lines in the .ino file.
def update_wifi_credentials_in_ino(ssid, password):
    # Creates a variable for the ino files and its path.
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    # Open the ino files to be read.
    with open(ino_path, 'r') as file:
        code = file.read()

    # Error checking to make sure fields are in .ino file.
    if 'const char* ssid =' not in code or 'const char* password =' not in code:
        print(" Could not locate ssid/password fields. Make sure the .ino file has the expected format.")
        return

    # In the .ino file, change the ssid and password fields of current connected network.
    updated_code = re.sub(r'const char\* ssid = ".*?";', f'const char* ssid = "{ssid}";', code)
    updated_code = re.sub(r'const char\* password = ".*?";', f'const char* password = "{password}";', updated_code)

    # Write to file.
    with open(ino_path, 'w') as file:
        file.write(updated_code)

    print(f" Wi-Fi ssid and password updated in {ino_file}")


## @brief Updates the Arduino sketch with Eduroam-specific login credentials.
#  @param ssid Eduroam SSID.
#  @param password Eduroam password.
#  @param eduroam_username University email used for Eduroam.
#  @param eduroam_identity Same as username (unless configured otherwise).
#  @details Updates 4 fields in the sketch: ssid, password, eduroam_username, and eduroam_identity.
def update_wifi_credentials_eduroam_in_ino(ssid, password, eduroam_username, eduroam_identity):
    # Creates a variable for the ino files and its path.
    ino_file = [f for f in os.listdir(esp32_sketch_path) if f.endswith(".ino")][0]
    ino_path = os.path.join(esp32_sketch_path, ino_file)

    # Open the ino files to be read.
    with open(ino_path, 'r') as file:
        code = file.read()

    # Error checking to make sure fields are in .ino file.
    if 'const char* ssid =' not in code or 'const char* password =' not in code or "const char* eduroam_username" not in code or "const char* eduroam_identity" not in code:
        print(" Could not locate ssid/password fields. Make sure the .ino file has the expected format.")
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

    print(f" Wi-Fi ssid and password updated in {ino_file}")


## @brief Clears SSID, password, and Eduroam credentials from the .ino file.
#  @details Used as a cleanup step after uploading to remove sensitive data.
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

    print(" Wi-Fi credentials cleared from .ino file.")

## @brief Compiles and uploads the Arduino sketch to ESP32 using arduino-cli.
#  @details Runs two subprocesses: one to compile and another to upload to the specified port.
def compile_and_upload():
    print(" Compiling sketch...")
    compile_cmd = ["arduino-cli", "compile", "--fqbn", esp32_board, esp32_sketch_path]
    subprocess.run(compile_cmd, check=True)

    print(" Uploading to ESP32...")
    upload_cmd = ["arduino-cli", "upload", "-p", esp32_port, "--fqbn", esp32_board, esp32_sketch_path]
    subprocess.run(upload_cmd, check=True)

    print(" Upload complete!")


## @brief Opens serial port, listens to ESP32, and logs weather data to CSV.
#  @details Continuously logs sensor output until interrupted (Ctrl+C).
def gather_local_weather():
    date_str = datetime.now().strftime("%d-%m-%Y")
    os.makedirs(localWeatherFolder, exist_ok=True)
    filename = os.path.join(localWeatherFolder, f"{date_str}.csv")

    ser = serial.Serial(esp32_port, 9600, timeout=1)
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Humidity (%)', 'Temp (C)', 'Temp (F)', 'Light Level (eV)', 'Brightness'])

        print("📡 Listening to ESP32 serial output... Press Ctrl+C to stop.")
        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"ESP32: {line}")
                    parts = line.split(',')
                    if len(parts) == 5:
                        timestamp = datetime.now().isoformat(timespec='seconds')
                        writer.writerow([timestamp, *[p.strip() for p in parts]])
                        csv_file.flush()

        except KeyboardInterrupt:
            print(" Data logging stopped.")
        finally:
            ser.close()
            clear_wifi_credentials()


## @brief Main entry point: handles SSID selection, updates .ino, uploads, and logs data.
#  @details Supports Eduroam and open networks. Handles SSID detection, prompting, and all data flow.
def _main():
    clear_wifi_credentials()
    ssid, wifi_password = get_current_network_credentials(None)
    if not ssid:
        print(" Could not detect SSID automatically.")
        available_ssids = list_ssid()

        if not available_ssids:
            print(" No networks found.")
            return

        print("\n Available Networks:")
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
                    print("Invalid selection. Please choose a valid number.")
            except ValueError:
                print(" Please enter a number.")
    else:
        print(f" Detected network: {ssid}")

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


if __name__ == '__main__':
    _main()
