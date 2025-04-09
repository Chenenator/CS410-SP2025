from dataclasses import dataclass
import requests
#import os

@dataclass
class WeatherInfo:
    city: str
    cloud_base: float
    cloud_ceiling: float
    cloud_cover: int
    dew_point: float
    freezing_rain_intensity: int
    precipitation_probability: int
    pressure_surface_level: float
    rain_intensity: float
    sleet_intensity: float
    snow_intensity: float
    temperature_apparent: float
    uv_health_concern: int
    uv_index: int
    visibility: float
    wind_direction: int
    wind_gust: float
    wind_speed: float

class WeatherApi:
    """
    Class for interacting with the Tomorrow.io Weather API.
    Provides basic functionality for making requests to the API
    """
    BASE_URL = "https://api.tomorrow.io/v4/weather/realtime?location="
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather_data(self, city, units):
        """
        Fetch weather data for a given city.
        :param city: Location (e.g., "Boston Massachusetts") as a string.
        :param units: Units for weather data (default: "metric").
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
    Inherits basic API functionality from WeatherApi.
    """
    @staticmethod
    def convert_wind_direction (degrees: int) -> str:
        """
        Convert wind direction in degrees to a compass direction (e.g., N, NE, E, etc.).

        :param degrees: Wind direction in degrees (0 to 360).
        :return: Compass direction as a string.
        """

        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        idx = round(degrees / 45) % 8
        return directions[idx]

    def parse_weather_data(self, weather_data):
        """
        Parse and populate the WeatherInfo dataclass from API response data.

        :param weather_data: The JSON response containing weather information.
        :return: Instance of WeatherInfo containing parsed weather data.
        """
        try:
            values = weather_data["data"]["values"]
            city = weather_data["location"]["name"]

            return WeatherInfo(
                city=city,
                cloud_base=values['cloudBase'],
                cloud_ceiling=values["cloudCeiling"],
                cloud_cover=values['cloudCover'],
                dew_point=values['dewPoint'],
                freezing_rain_intensity=values['freezingRainIntensity'],
                precipitation_probability=values['precipitationProbability'],
                pressure_surface_level=values['pressureSurfaceLevel'],
                rain_intensity=values['rainIntensity'],
                sleet_intensity=values['sleetIntensity'],
                snow_intensity=values['snowIntensity'],
                temperature_apparent=values['temperatureApparent'],
                uv_health_concern=values['uvHealthConcern'],
                uv_index=values['uvIndex'],
                visibility=values['visibility'],
                wind_direction=values['windDirection'],
                wind_gust=values['windGust'],
                wind_speed=values['windSpeed']
            )
        except KeyError:
            print("Error: Unexpected response format.")
            return None

    def display_weather_data(self, weather_info: WeatherInfo, units: str):
        """
        Display weather information stored in a WeatherInfo dataclass instance.

        :param weather_info: Instance of WeatherInfo containing weather details.
        """
        # Convert wind direction before displaying
        compass_direction = self.convert_wind_direction(weather_info.wind_direction)
        # Determine the correct units for display
        if units == "metric":
            temp_unit = "°C"
            speed_unit = "km/h"
            distance_unit = "km"
            pressure_unit = "hPa"
            precipation_measure = "mm"
        else:
            temp_unit = "°F"
            speed_unit = "mph"
            distance_unit = "miles"
            pressure_unit = "hPa"
            precipation_measure = "in"

        if weather_info:
            print(f"Weather Data for {weather_info.city}:")
            print(f"  Cloud Base: {weather_info.cloud_base} {distance_unit}")
            print(f"  Cloud Ceiling: {weather_info.cloud_ceiling} {distance_unit}")
            print(f"  Cloud Cover: {weather_info.cloud_cover}%")
            print(f"  Dew Point: {weather_info.dew_point:.1f} {temp_unit}")
            print(f"  Freezing Rain Intensity: {weather_info.freezing_rain_intensity}%")
            print(f"  Precipitation Probability: {weather_info.precipitation_probability}%")
            print(f"  Pressure Surface Level: {weather_info.pressure_surface_level} {pressure_unit}")
            print(f"  Rain Intensity: {weather_info.rain_intensity} {precipation_measure}")
            print(f"  Sleet Intensity: {weather_info.sleet_intensity} {precipation_measure}")
            print(f"  Snow Intensity: {weather_info.snow_intensity} {precipation_measure}")
            print(f"  Apparent Temperature: {weather_info.temperature_apparent:.1f} {temp_unit}")
            print(f"  UV Health Concern: {weather_info.uv_health_concern}")
            print(f"  UV Index: {weather_info.uv_index}")
            print(f"  Visibility: {weather_info.visibility:.1f} {distance_unit}")
            print(f"  Wind Direction: {weather_info.wind_direction}° ({compass_direction})")
            print(f"  Wind Gust: {weather_info.wind_gust:.1f} {speed_unit}")
            print(f"  Wind Speed: {weather_info.wind_speed:.1f} {speed_unit}")
        else:
            print("No weather information available.")



def main():
    api_key = "iR7AB19TwE1p5yFXW41OmAdQ8wFqAEAc"
    if not api_key:
        print("Error: TOMORROW.IO API KEY not set.")
        return
    city = input("Enter the name of the city: ")
    units = input("Enter units (metric or imperial): ").lower()

    if units not in ["metric", "imperial"]:
        print("Invalid units. Defaulting to metric.")
        units = "metric"
        weather = WeatherData(api_key)
        weather_data = weather.get_weather_data(city, units)

        if weather_data:
            weather_info = weather.parse_weather_data(weather_data)
            weather.display_weather_data(weather_info, units)
        return

    weather = WeatherData(api_key)
    # Get the weather data from api
    weather_data = weather.get_weather_data(city, units)
    if weather_data:
        # Call the extract_weather_data method
        weather_info = weather.parse_weather_data(weather_data)
        # Pass the extracted data into the display_weather_data method
        weather.display_weather_data(weather_info, units)
    else:
        print("Error: Failed to fetch weather data.")

if __name__ == "__main__":
    main()
