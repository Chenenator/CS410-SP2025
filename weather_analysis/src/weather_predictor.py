## @file weather_predictor.py
#  @brief Predicts future temperatures using Ridge regression and sends forecast to ThingsBoard.
#  @details Loads historical weather data, predicts future tmax and tmin, and optionally sends results
#  to Thingsboard.

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge  # Ridge regression model
import requests
from datetime import datetime

## @class WeatherPredictor
#  @brief Predicts future weather (max/min temperatures) using Ridge regression.
#  @details
#  The class loads and preprocesses weather data, creates lagging and rolling features,
#  fits a Ridge regression model, and performs sequential prediction for a specified number of days.
class WeatherPredictor:

    ## @brief Constructor to initialize data path and model.
    #  @param data_path: Path to the CSV file containing historical weather data.
    #  @details Initializes the internal Ridge regression model and stores the path to the dataset.
    def __init__(self, data_path):
        self.data_path = data_path
        self.weather_data = None
        self.model = Ridge(alpha=0.1)  # Ridge regression model

    ## @brief Loads the weather CSV and prepares features for training.
    #  @details
    #  - Loads weather data into a DataFrame.
    #  - Fills missing values and removes low-quality columns.
    #  - Shifts tmax/tmin columns to create targets for next-day prediction.
    #  - Computes rolling averages and grouped expanding averages.
    def load_and_prepare_data(self):
        # Load the weather data CSV into DataFrame and clean it
        self.weather_data = pd.read_csv(self.data_path, index_col="DATE")
        self.weather_data.columns = self.weather_data.columns.str.lower()  # Optional

        #Convert index to data type
        self.weather_data.index = pd.to_datetime(self.weather_data.index, errors="coerce")
        self.weather_data = self.weather_data.ffill()  # Fill missing data

        # Remove columns with more than 5% missing values
        null_percentage = self.weather_data.apply(pd.isnull).sum() / self.weather_data.shape[0]
        valid_columns = self.weather_data.columns[null_percentage < 0.05]
        self.weather_data = self.weather_data[valid_columns].copy()

        # Create target columns for prediction (next day's max and min temperature)
        self.weather_data[["maxtemp", "mintemp"]] = self.weather_data[["tmax", "tmin"]].shift(-1)
        self.weather_data = self.weather_data.drop(columns=["station", "name"], errors="ignore")

        # Add rolling average feature
        for horizon in [3, 14]:
            for col in ["tmax", "tmin", "prcp"]:
                self.compute_rolling(horizon, col)

        self.weather_data = self.weather_data.iloc[14:, :]  # Drop initial rows with NaNs
        self.weather_data.fillna(0, inplace=True)

        # Add expanding (cumulative mean) averages by month and day of year
        for col in ["tmax", "tmin", "prcp"]:
            self.weather_data[f"month_avg_{col}"] = self.weather_data[col].groupby(
                self.weather_data.index.month, group_keys=False).apply(lambda x: x.expanding(1).mean())
            self.weather_data[f"day_avg_{col}"] = self.weather_data[col].groupby(
                self.weather_data.index.day_of_year, group_keys=False).apply(lambda x: x.expanding(1).mean())

        # Final clean up
        self.weather_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.weather_data.fillna(0, inplace=True)

    ## @brief Adds rolling average and percent difference for a given feature.
    #  @param horizon: Number of days in rolling window.
    #  @param col: Column to compute rolling average on.
    #  @details Computes both the rolling mean and relative percentage change for use as features.
    def compute_rolling(self, horizon, col):
        # Compute rolling average and percentage difference for the given column
        label = f"rolling_{horizon}_{col}"
        self.weather_data[label] = self.weather_data[col].rolling(horizon).mean()
        self.weather_data[f"{label}_percentage"] = (self.weather_data[label] - self.weather_data[col]) / \
                                                   self.weather_data[col]

    ## @brief Returns list of predictor column names (excluding target variables).
    #  @return list of strings representing feature columns used for training/prediction.
    #  @details Excludes columns like max temp/min temp/station/name from predictors.
    def get_predictors(self):
        # Get list of predictor column names, excluding target and ID columns
        excluded = ["maxtemp", "mintemp", "name", "station"]
        return self.weather_data.columns[~self.weather_data.columns.isin(excluded)]

    ## @brief Predicts max and min temperatures for the next N days.
    #  @param days Number of future days to forecast.
    #  @return list of dictionaries containing forecasted date, maxTemp, and minTemp.
    #  @details
    #  Performs recursive forecasting by using predicted values from the previous day
    #  as input for the next day's prediction.
    def predict_next_days(self, days):
        # Predict the next N days of max and min temperature
        predictors = self.get_predictors()
        last_known = self.weather_data.copy()
        predictions = []

        for _ in range(days):
            input_row = last_known.iloc[-1:][predictors]  # Use last known data for prediction

            self.model.fit(last_known[predictors], last_known["maxtemp"])
            predicted_max = self.model.predict(input_row)[0]  # predict max temp

            self.model.fit(last_known[predictors], last_known["mintemp"])
            predicted_min = self.model.predict(input_row)[0]  # predict min temp

            prediction_date = last_known.index[-1] + pd.Timedelta(days=1)

            # Save prediction in a dictionary
            predictions.append({
                "date": prediction_date.strftime("%Y-%m-%d"),
                "maxTemp": predicted_max,
                "minTemp": predicted_min
            })
            # Simulate new row for the next prediction iteration
            new_row = last_known.iloc[-1:].copy()
            new_row.index = [prediction_date]
            new_row["tmax"] = predicted_max
            new_row["tmin"] = predicted_min
            new_row["maxtemp"] = predicted_max
            new_row["mintemp"] = predicted_min
            last_known = pd.concat([last_known, new_row])

        return predictions

    ## @brief Prepares data and runs prediction.
    #  @param days Number of days to forecast.
    #  @return list of forecast results for each day.
    #  @details This is the main method to call for a complete forecast workflow.
    def get_N_day_forecast(self, days):
        #  Main method to load data and return n-day forecast
        self.load_and_prepare_data()
        return self.predict_next_days(days)

    ## @brief Plots historical Tmax and Tmin from the dataset.
    #  @details
    #  Displays a time series graph of the two temperature metrics.
    def plot_temperature_trend(self):
        # Plot historical temperature trends for both Tmax and Tmin with red line for clarity
        if self.weather_data is None:
            self.load_and_prepare_data()

        plt.figure(figsize=(14, 7))
        plt.plot(self.weather_data.index, self.weather_data["tmax"], label="Tmax", color="red")
        plt.plot(self.weather_data.index, self.weather_data["tmin"], label="Tmin", color="blue")
        plt.title("Historical Tmax and Tmin Over Time")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°F)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

## @brief Sends forecasted weather data to ThingsBoard via REST API.
#  @param forecast List of dictionaries with forecasted max/min temperatures.
#  @param token ThingsBoard device access token.
#  @details
#  Converts each day's forecast into a timestamped JSON payload and posts it individually
#  to ThingsBoard cloud using HTTP POST to the device telemetry endpoint.
def send_to_thingsboard(forecast, token):
    url = f"https://thingsboard.cloud/api/v1/{token}/telemetry"

    for day in forecast:
        # Convert forecast date to timestamp in milliseconds
        timestamp = int(datetime.strptime(day["date"], "%Y-%m-%d").timestamp() * 1000)

        payload = {
            "ts": timestamp,
            "values": {
                "Predicted maxTemp": round(day["maxTemp"], 2),
                "Predicted minTemp": round(day["minTemp"], 2)
            }
        }

        # Send each day's payload separately
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"Error sending data for {day['date']}: {response.status_code} {response.text}")
        else:
            print(f"Sent prediction for {day['date']}")

## @brief Main script entry point.
#  @details
#  Initializes the WeatherPredictor with a CSV file, generates a multi-day forecast,
#  prints the results, and sends them to ThingsBoard.
if __name__ == "__main__":
    # path to bostonweather.csv
    data_file_path = os.path.join(os.path.dirname(os.getcwd()), "data", "bostonweather.csv")

    predictor = WeatherPredictor(data_file_path)
    DAYS = 5
    forecast = predictor.get_N_day_forecast(DAYS)

    print("Future Day Forecast:")
    for day in forecast:
        print(f"{day['date']}: Max {day['maxTemp']:.2f}°F, Min {day['minTemp']:.2f}°F")

    ACCESS_TOKEN = "RdUYWvQYczLFV5zSfziq"
    send_to_thingsboard(forecast, ACCESS_TOKEN)
