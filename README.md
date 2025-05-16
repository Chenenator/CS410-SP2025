# 🌦️ ESP32 IoT Weather Station with AI Forecasting

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![ESP32](https://img.shields.io/badge/Board-ESP32-orange?logo=arduino)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blueviolet)]()
[![ML Model](https://img.shields.io/badge/ML-Ridge%20Regression-lightgrey?logo=scikit-learn)](https://scikit-learn.org/)

This is a smart, connected weather station powered by an ESP32 board and various sensors. It collects real-time environmental data, sends it to a dashboard, and uses AI to predict future weather trends based on historical data.

---

## 🚀 Features

- 📡 **Real-time Weather Logging** (Humidity, Temp °C/°F, Light)
- 🔧 **Automatic Wi-Fi Config & ESP32 Upload**
- 📊 **Local CSV Logging & Cloud Integration**
- 🧠 **AI Weather Forecasting (Ridge Regression)**
- 📉 **Backtesting & Performance Evaluation**
- 📺 **Support for Eduroam/WPA2 Enterprise**

---

## 🧰 Hardware Components

| Component         | Description                      |
|------------------|-----------------------------------|
| ESP32-WROVER Kit | Main microcontroller              |
| DHT11            | Humidity and Temperature Sensor   |
| LM35             | Analog Temperature Sensor         |
| Photocell (LDR)  | Light Intensity Detection         |
| LCD (Optional)   | Display module via I2C            |

---

## 📖 Manual

### 🔌 1. Hardware Setup
  -  DHT11 Humidity Sensor:
      * G Pin -> Ground Slot
      * V Pin -> 3V3 Slot
      * S Pin -> D4 Slot
  -  LM35 Temperature Sensor:
      * G Pin -> Ground Slot
      * V Pin -> VIN Slot
      * S Pin -> D35 Slot
  -  Photocell Sensor:
      * G Pin -> Ground Slot
      * V Pin -> 3V3 Slot
      * S Pin -> D34 Slot

---

### 🖥️ 2. Software Requirements

- Python 3.10+
- [Arduino CLI](https://arduino.github.io/arduino-cli/)
- Install Python dependencies:
  ```bash
  
  pip install -r requirements.txt

---

### ⚙️ 3. Initial Setup

Install ESP32 Board in Arduino CLI:
 ```bash
  arduino-cli core install esp32:esp32
```
Compile & Upload Firmware:

Run the GUI or directly execute:

    python src/weather_analysis/weather_gui_launcher.py

Wi-Fi Credentials:

- Auto-detects and updates .ino with current SSID and password

- Eduroam/WPA2-Enterprise support with prompt for university credentials

Additional Setup Considerations:

- A cloud to record all numerical data (e.g. ThingsBoard)
- A web host to display data for the public to see
- A proxy server for any backend tasks, such as requesting data from the cloud (e.g. Microsoft Azure)

---

### 🖱️ 4. Launch GUI

Run with Python:

```bash
python src/weather_analysis/weather_gui_launcher.py
```

### 💡 5. How to Use

- Navigation Bar:
    * Weather: Clicking on this brings you to the Weather Section.
    * Dashboard: Clicking on this brings you to the the first dashboard in the Dashboard Section, the Temperature and Humidity time graph.
    * GitHub: Clicking on this brings you to the GitHub repository.
    * Moon toggle: Switches theme to light or dark mode. Refresh to see the switch automatically toggle on or off based on brightness level.

- Weather Section:
    * Shows basic numerical readings of temperature, humidity, brightness, and "feels like" temperature.

- Dashboard Section:
    * Temp and Humidity: Displays the time graph of temperature and humidity. Use this to see the trends of temperature and humidity.
    * Weather Predictor: Displays time graph of the predicted high and low temperatures of the next few days.
