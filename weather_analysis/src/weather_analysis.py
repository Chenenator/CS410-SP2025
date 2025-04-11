import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


class WeatherAnalyzer:
    def __init__(self):
        self.weather = pd.read_csv("//data/bostonweather.csv",
                                index_col="DATE")

    # Get the raw data with all columns.
    def raw_data(self):
        return self.weather

    # Get the data only pertaining to the five most relevent factors.
    def prepare_data(self):
        nullPcnt = self.weather.apply(pd.isnull).sum() / self.weather.shape[0]
        print()
        ...


def _main():
    weather = WeatherAnalyzer()
    weather.prepare_data()


if __name__ == '__main__':
    _main()
