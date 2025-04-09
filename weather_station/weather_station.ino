/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-dht11
 */

#include <DHT.h>
#define DHT11_PIN 4 // ESP32 pin GPIO21 connected to DHT11 sensor
DHT dht11(DHT11_PIN, DHT11);

#define ADC_VREF_mV    3300.0 // in millivolt
#define ADC_RESOLUTION 4096.0
#define PIN_LM35       35 // ESP32 pin GPIO36 (ADC0) connected to LM35

void setup() {
  Serial.begin(9600);
  delay(2000);
  dht11.begin(); // initialize the DHT11 sensor

  // set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
}

void loop() {
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
  }
  // wait a 2 seconds between readings
  delay(2000);
}
