## @file weather_analysis.py
#  @brief Loads and inspects historical weather data from Boston.
#  @details
#  This module defines a class to load a weather CSV file, inspect for missing values,
#  and return raw data for analysis or processing. Useful for quick data quality checks.

import pandas as pd
import os

## @class WeatherAnalyzer
#  @brief A class to load historical weather data from Boston.
#  @details Loads weather data from a CSV file and provides basic data inspection and preparation functions.
class WeatherAnalyzer:
    ## @brief Constructor that loads the weather data CSV into a pandas DataFrame.
    #  @details The CSV file must be located at ../data/bostonweather.csv relative to the current working directory.

    def __init__(self):
        ## @var self.weather
        #  @brief Pandas DataFrame containing the loaded weather data.
        #  @note The 'DATE' column is used as the DataFrame index.
        self.weather = pd.read_csv(os.path.dirname(os.getcwd()) + "/data/bostonweather.csv",
                                index_col="DATE")

    ## @brief Returns the raw weather DataFrame.
    #  @return pandas.DataFrame with all columns and rows from the weather CSV.
    def raw_data(self):
        return self.weather

    ## @brief Prints percentage of null values for each column.
    #  @details This function calculates the fraction of missing values per column
    #  and is intended to help in determining relevant data features.
    def prepare_data(self):
        ## @var nullPcnt
        #  @brief Series containing the percentage of null values per column.
        nullPcnt = self.weather.apply(pd.isnull).sum() / self.weather.shape[0]
        #self.weather.apply(pd.isnull).sum() / self.weather.shape[0]

## @brief Main entry point for standalone testing.
#  @details Instantiates the class and calls the `prepare_data()` method to print null stats.
def _main():
    weather = WeatherAnalyzer()
    weather.prepare_data()

if __name__ == '__main__':
    _main()
