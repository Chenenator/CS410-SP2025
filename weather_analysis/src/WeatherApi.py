import requests
#import os

class WeatherApi:
    """
    Class for interacting with the Tomorrow.io Weather API.
    Provides basic functionality for making requests to the API
    """
    BASE_URL = "https://api.tomorrow.io/v4/weather/realtime?location="
    def __init__(self, api_key):
        self.api_key = api_key

    def get_miscellaneous_weather_data(self, city, units= "imperial"):
        """
        Fetch weather data for a given city.
        :param city: Location (e.g., "Boston Massachusetts") as a string.
        :param units: Units for weather data (default: "imperial").
        :return: JSON response or None if request fails.
        """
        # Construct API URL
        formatted_city = city.replace(" ", "%20")
        url = f"{self.BASE_URL}{formatted_city}&units={units}&apikey={self.api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Failed to fetch weather data. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None

class WeatherData(WeatherApi):
 """
 Derived class for handling and displaying weather data.
 Inherits basic API functionality from WeatherAPI.
 """

 def display_weather_data(self, weather_data):
     """
     Extract and display miscellaneous weather information.

     :param weather_data: The JSON response containing weather information.
     """
     try:
         values = weather_data["data"]["values"]

         print("Weather Data:")
         print(f"Cloud Base: {values['cloudBase']} km")
         print(f"Cloud Ceiling: {values['cloudCeiling']} km")
         print(f"Cloud Cover: {values['cloudCover']}%")
         print(f"Dew Point: {values['dewPoint']} °F")
         print(f"Freezing Rain Intensity: {values['freezingRainIntensity']}%")
         print(f"Precipitation Probability: {values['precipitationProbability']}%")
         print(f"Pressure Surface Level: {values['pressureSurfaceLevel']} hPa")
         print(f"Rain Intensity: {values['rainIntensity']} mm/hr")
         print(f"Sleet Intensity: {values['sleetIntensity']} mm/hr")
         print(f"Snow Intensity: {values['snowIntensity']} mm/hr")
         print(f"Apparent Temperature: {values['temperatureApparent']} °F")
         print(f"UV Health Concern: {values['uvHealthConcern']}")
         print(f"UV Index: {values['uvIndex']}")
         print(f"Visibility: {values['visibility']} miles")
         print(f"Wind Direction: {values['windDirection']}°")
         print(f"Wind Gust: {values['windGust']} mph")
         print(f"Wind Speed: {values['windSpeed']} mph")

     except KeyError:
         print("Error: Unexpected response format.")
         print(weather_data)

def main():
    api_key = "iR7AB19TwE1p5yFXW41OmAdQ8wFqAEAc"
    if not api_key:
        print("Error: TOMORROW.IO API KEY not set.")
        return
    city = input("Enter the name of the city: ")
    weather = WeatherData(api_key)
    weather_data = weather.get_miscellaneous_weather_data(city)
    if weather_data:
        weather.display_weather_data(weather_data)
    else:
        print("Error: Failed to fetch weather data.")

if __name__ == "__main__":
    main()
