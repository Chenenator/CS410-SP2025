## @file Weather_api.py
#  @brief Fetches and displays real-time weather data using Tomorrow.io API.
#  @details
#  This script allows users to input a city name and fetch its current weather
#  metrics using the Tomorrow.io REST API. It prints detailed conditions such as
#  temperature, wind, precipitation, and visibility.
#  @note Useful for future improvements on this project.

import requests


## @class WeatherApi
#  @brief A class for interacting with the Tomorrow.io Weather API.
#  @details Provides basic functionality for making real-time weather API requests.
class WeatherApi:
    ## @var BASE_URL
    #  @brief Base URL for the Tomorrow.io real-time weather API.
    BASE_URL = "https://api.tomorrow.io/v4/weather/realtime?location="

    ## @brief Constructor to initialize the API key.
    #  @param api_key The API key for authenticating with Tomorrow.io.
    #  @note Change the api key in main() if the old one is not working.
    def __init__(self, api_key):
        self.api_key = api_key

    ## @brief Fetch miscellaneous weather data for a given city.
    #  @param city The name of the city (e.g., "Boston Massachusetts").
    #  @param units The units of measurement (default is "imperial").
    #  @return JSON response from the API or None if request fails.
    def get_miscellaneous_weather_data(self, city, units="imperial"):
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


## @class WeatherData
#  @brief A subclass of WeatherApi to process and display weather data.
#  @details Inherits API access from WeatherApi and adds methods to extract and present weather metrics.
class WeatherData(WeatherApi):

    ## @brief Extract and display various weather metrics from the API response.
    #  @param weather_data The JSON object returned from the API call.
    #  @return None
    def display_weather_data(self, weather_data):
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


## @brief Main entry point of the script.
#  @details Prompts user for a city, fetches and displays its weather data using Tomorrow.io API.
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
