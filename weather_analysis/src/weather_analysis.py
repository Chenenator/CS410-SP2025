import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


class WeatherAnalyzer:
    def __init__(self):
        self.data = pd.read_csv("//data/bostonweather.csv",
                                index_col="DATE")

    # Get the raw data with all columns.
    def raw_data(self):
        return self.data

    # Get the data only pertaining to the five most relevent factors.
    def prepare_data(self):
        core_weather = self.data[["PRCP", "SNOW", "SNWD", "TMAX", "TMIN"]].copy()
        core_weather.columns = ["precipitation", "snow", "snow_depth", "temp_max", "temp_min"]

        nullPercent = (core_weather.apply(pd.isnull).sum() / core_weather.shape[0])
        print(nullPercent)

        columns_to_drop = [col for col in core_weather if core_weather[col].count() < 10]
        core_weather = core_weather.drop(columns_to_drop)
        return core_weather


def _main():
    weather = WeatherAnalyzer()
    raw_data = weather.raw_data()
    raw_data.apply(pd.isnull).sum()
    print(raw_data)
    weather.prepare_data()


if __name__ == '__main__':
    _main()
