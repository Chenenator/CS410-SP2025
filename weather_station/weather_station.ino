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
#include <ThingsBoard.h>
#include <Arduino_MQTT_Client.h>
#include <ArduinoJson.h>

const char* ssid = "DennisWifi";
const char* password = "connectionMeme52@yay!";

#define DHT11_PIN 4 // ESP32 pin GPIO21 connected to DHT11 sensor
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

void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}

/// @brief Reconnects the WiFi uses InitWiFi if the connection has been removed
/// @return Returns true as soon as a connection has been established again
const bool reconnect() {
  // Check to ensure we aren't connected yet
  const wl_status_t status = WiFi.status();
  if (status == WL_CONNECTED) {
    return true;
  }

  // If we aren't establish a new connection to the given WiFi network
  initWiFi();
  return true;
}

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

void sendDataToThingsBoard(float tempC, float tempF, int humi) {
  StaticJsonDocument<256> jsonDoc;

  jsonDoc["tempIn"] = tempC;
  jsonDoc["humIn"] = humi;

  tb.sendTelemetryJson(jsonDoc, measureJson(jsonDoc));
  Serial.println("Data sent");
}

void setup() {
  Serial.begin(9600);
  delay(2000);
  dht11.begin(); // initialize the DHT11 sensor

  // set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);

  initWiFi();
  Serial.print("RRSI: ");
  Serial.println(WiFi.RSSI());
}

void loop() {
  // wait a 1 seconds between readings
  delay(1000);

  if (!reconnect) return;
  if (!tb.connected()) {
    connectToThingsBoard();
  }
  // read humidity
  float humi  = dht11.readHumidity();

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
    Serial.println(tempF, 1);
    sendDataToThingsBoard(tempC, tempF, humi);
  }
  tb.loop();
}