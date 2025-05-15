/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-dht11

    Packages:
    - DHT sensor library by Adafruit
    - DHTlib by Rob Tillaart
    - ThingsBoard by ThingsBoard Team
    - ArduinoMgttClient by Arduino
    - ArduinoJson by Benoit Blanchon
    - PubSubClient by Nick O'Leary
    - TBPubSubClient by ThingsBoard
 */

#include <DHT.h>
#include <WiFi.h>
#include "esp_wpa2.h" // Needed for WPA2-Enterprise
#include <WiFiManager.h>
#include <ThingsBoard.h>
#include <Arduino_MQTT_Client.h>
#include <ArduinoJson.h>

const char* ssid = "SSID";
const char* password = "PASSWORD";

const char* eduroam_username = "UNIVERSITY_EMAIL";
const char* eduroam_identity = "UNIVERSITY_EMAIL"; // often same as username

#define DHT11_PIN 4 // ESP32 pin GPIO21 connected to DHT11 sensor
#define LIGHT_SENSOR_PIN 34
DHT dht11(DHT11_PIN, DHT11);

#define ADC_VREF_mV    3300.0 // in millivolt
#define ADC_RESOLUTION 4096.0
#define PIN_LM35       35 // ESP32 pin GPIO36 (ADC0) connected to LM35

#define TB_SERVER "thingsboard.cloud"
#define TOKEN "ivcoixXiUzBWe0zdNtjv"
// MQTT port used to communicate with the server, 1883 is the default unencrypted MQTT port.
constexpr uint16_t TB_PORT = 1883U;

constexpr uint16_t MAX_MESSAGE_SIZE = 1024U;

WiFiClient espClient;
Arduino_MQTT_Client mqttClient(espClient);
ThingsBoard tb(mqttClient, MAX_MESSAGE_SIZE);

// WiFi connection with timeout and better status handling
/**
* @brief Connects esp32 to wifi with error handeling
*
* @details
* Connects to wifi network using ssid and password provided
* This connection has timeout and status handeling functionality
*
*/
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal strength (RSSI): ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}
/**
* @brief Arduino code for conecting sensor data to thingsboard over Eduroam wifi
*
* @details
* Disconects previous wifi connection and enables WPA2-enterprise to allow 
* connection with school wifi
*/
void initEduroamWiFi() {
  WiFi.disconnect(true); // Disconnect previous WiFi
  WiFi.mode(WIFI_STA);
  esp_wifi_sta_wpa2_ent_enable(); // Enable WPA2-Enterprise
  esp_wifi_sta_wpa2_ent_set_identity((uint8_t *)eduroam_identity, strlen(eduroam_identity));
  esp_wifi_sta_wpa2_ent_set_username((uint8_t *)eduroam_username, strlen(eduroam_username));
  esp_wifi_sta_wpa2_ent_set_password((uint8_t *)password, strlen(password));
  
  WiFi.begin("eduroam");

  Serial.println("Connecting to Eduroam...");

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(1000);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to Eduroam!");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to Eduroam.");
  }
}

// Fixed reconnect function
/**
* @brief Function for reconnecting to the wifi
*
* @details
* This code checks the wifi status and attempts to reconect if disconected
*/
bool reconnect() {
  const wl_status_t status = WiFi.status();
  if (status == WL_CONNECTED) {
    return true;
  }

  Serial.println("WiFi connection lost. Reconnecting...");
  // Try to reconnect
  (ssid == "eduroam") ? initEduroamWiFi() : initWiFi();
  // Return actual connection status after attempt
  return (WiFi.status() == WL_CONNECTED);
}
/**
* @brief Fuction for creating a connection to ThingsBoard
*
* @details
* connects esp32 to Things board to transfer data to the cloud
* using TB_SERVER, TOKEN, and TB_PORT
*/
void connectToThingsBoard() {
    // Connect to the ThingsBoard
    Serial.print("Connecting to: ");
    Serial.print(TB_SERVER);
    Serial.print(" with token ");
    Serial.println(TOKEN);
    if (!tb.connect(TB_SERVER, TOKEN, TB_PORT)) {
      Serial.println("Failed to connect");
      return;
    }
    // Sending a MAC address as an attribute
    tb.sendAttributeData("macAddress", WiFi.macAddress().c_str());

}
/**
* @brief Function for sending data from esp32 to ThingsBoard
*
* @param tempC The temperature in Celcius
* @param tempF The temperature in Ferinheight
* @param humi The humidity presentage
* @param light The light level
* @param brightness The brightneess
*
* @details
* This function takes weather variables as parameters and sends them to the ThingsBoard cloud
*/
void sendDataToThingsBoard(float tempC, float tempF, int humi, int light, String brightness) {
  StaticJsonDocument<256> jsonDoc;

  jsonDoc["TempC"] = tempC;
  jsonDoc["TempF"] = tempF;
  jsonDoc["Humidity"] = humi;
  jsonDoc["Light"] = light;
  jsonDoc["Brightness"] = brightness;

  tb.sendTelemetryJson(jsonDoc, measureJson(jsonDoc));
  Serial.println("Data sent");
}

/**
* @brief Fuction for setting up environment for sensors and esp32
*
* @details
* This function initializes the DHT11 sensor, sets timeout for config portal,
* and creates an accesspoint called "WeatherStation" if it can't connect to wifi
*/
void setup() {
  Serial.begin(9600);
  delay(2000);
  dht11.begin(); // initialize the DHT11 sensor

  // set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);

  (ssid == "eduroam") ? initEduroamWiFi() : initWiFi();
  Serial.print("RRSI: ");
  Serial.println(WiFi.RSSI());

  WiFiManager wifiManager;
  // Uncomment to reset saved settings
  // wifiManager.resetSettings();
  
  // Set timeout for configuration portal
  wifiManager.setConfigPortalTimeout(180);
  
  // Creates an access point named "WeatherStation" if can't connect to WiFi
  if(!wifiManager.autoConnect("WeatherStation")) {
    Serial.println("Failed to connect, restarting...");
    delay(3000);
    ESP.restart();
  }
  
  Serial.println("Connected to WiFi!");
}

/**
* @brief Fuction for reading sensor data
*
* @details
* This function loops to continually read sensor data at one second interval
*/
void loop() {
  // wait a 1 seconds between readings
  delay(1000);

  if (!reconnect()) return;
  if (!tb.connected()) {
    connectToThingsBoard();
  }
  // read humidity
  float humi  = dht11.readHumidity();

  // Read light sensor
  int lightValue = analogRead(LIGHT_SENSOR_PIN);
  String brightness = "";
  // We'll have a few threshholds, qualitatively determined
  if  (lightValue < 40) {
    brightness = "Dark";
  } else if  (lightValue < 800) {
    brightness = "Dim";
  } else if  (lightValue < 2000) {
    brightness = "Light";
  } else if  (lightValue < 3200) {
    brightness = "Bright";
  } else {
    brightness = "Very Bright";
  }
  
  // read the ADC value from the temperature sensor
  long adcVal = analogRead(PIN_LM35);
  // convert the ADC value to voltage in millivolt
  float milliVolt = adcVal * (ADC_VREF_mV / ADC_RESOLUTION);
  // convert the voltage to the temperature in °C
  float tempC = milliVolt / 10;
  // convert the °C to °F
  float tempF = tempC * 9 / 5 + 32;

  // check whether the reading is successful or not
  if (isnan(humi) || isnan(adcVal)) {
    Serial.println("Failed to read from DHT11 or LM35 sensor!");
  } else {
    // Print as CSV: humi,tempC,tempF
    Serial.print(humi, 1);
    Serial.print(",");
    Serial.print(tempC, 1);
    Serial.print(",");
    Serial.print(tempF, 1);
    Serial.print(",");
    Serial.print(lightValue, 1);
    Serial.print(",");
    Serial.println(brightness);
    sendDataToThingsBoard(tempC, tempF, humi, lightValue, brightness);
  }

  tb.loop();
}
