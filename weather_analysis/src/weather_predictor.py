import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge # Ridge regression model
from sklearn.metrics import mean_squared_error, mean_absolute_error # measuring accuracy

"""****************************************** Functions *****************************************"""
def getpredictors(weatherData):
    """
    getpredictors function: weather data frame -> return weather data frame
    Give all the columns in the weather data frame except these columns as predictors
    """
    excludedColumns = ["maxTemp","minTemp", "name", "station"]
    return weatherData.columns[~weatherData.columns.isin(excludedColumns)]

def backtest (weather, model, predictors, target_col, start = 20100, step = 90):
    """
    backtest function: weatherData, machine learning model, amount of data to take before making prediction,
    every x day to make prediction -> return a dataframe with actual and predicted temperature for each day.
    """
    all_predictions = []

    for i in range(start, weather.shape[0], step):
        train = weatherData.iloc[:i, :] # All the rows in our data up to row i to train the model
        test = weatherData.iloc[i:(i+step),:] # Take the next 90 days to make predictions on

        if not np.all(np.isfinite(test[predictors].values)):
            print(f"Non-finite values in test set at index {i}")
            print(test[predictors][~np.isfinite(test[predictors])])
            break

        model.fit(train[predictors], train[target_col]) # Fit model to the data
        preds = model.predict(test[predictors]) # Generate predictions, outputs numpy array
        preds = pd.Series(preds, index = test.index) # Convert it to panda series = easy to work with
        combined = pd.concat([test[target_col], preds], axis = 1) # Concatenate real test data with predictions
        combined.columns = ["actual",  "prediction"]
        combined["diff"] = (combined["prediction"] - combined["actual"].abs())
        combined["target"] = target_col
        all_predictions.append(combined)

    return pd.concat(all_predictions)


def percentagediff(old, new):
    """
    percentagediff function: old value, new value -> return percentage difference
    """
    return (new - old) / old

def computerolling(weather, horizon, col):
    """
    computerolling function: weather data frame, horizon, column name -> return weather data frame
    Compute rolling averages for each column in the weather data frame.
    """
    label = f"rolling_{horizon}_{col}"
    weather[label] = weather[col].rolling(horizon).mean()
    weather[f"{label}_percentage"] = percentagediff(weather[label], weather[col])
    return weather

def expandmean(df):
    """
    expandmean function: weather data frame -> return weather data frame
    Compute expanding averages for each column in the weather data frame.
    """
    return df.expanding(1).mean()

def updatecsv(weatherData):
    """
    updatecsv function: weather data frame -> save the weather data frame to a csv file
    """
    weatherData.to_csv("cleaned_weather_data.csv")




""" ************************************** Data Preparation **********************************"""

"""
Read the csv file containing the historical weather data
Use the panda read csv function
"""
weatherData = pd.read_csv(os.path.dirname(os.getcwd()) + "/data/bostonweather.csv", index_col="DATE")
#print(weatherData)

""" 
Remove any data containing NaN (Bad for machine learning model)
"""
nullPercentage = weatherData.apply(pd.isnull).sum() / weatherData.shape[0]
#print(nullPercentage)

"""
Clean up data, remove any column where the null percentage is too low (adjust accordingly)
"""
validColumns = weatherData.columns[nullPercentage <.05]
#print(validColumns)

"""
Change the data set, containing only the validColumns. Fill any missing values
"""
weatherData = weatherData[validColumns].copy()
weatherData.columns = weatherData.columns.str.lower() #Make column names lower case (optional)
weatherData = weatherData.ffill()
#print(weatherData.apply(pd.isnull).sum())

"""
Make sure data columns are correct data type and the index as well
"""
#print(weatherData.dtypes)
#print(weatherData.index)

"""
Convert index to data type
"""
weatherData.index = pd.to_datetime(weatherData.index, errors= "coerce")
#print(weatherData.index.year.value_counts().sort_index())
"""
Drop non-numeric columns and check for gaps in data. Too many gaps = less accurate prediction.
"""
weatherData = weatherData.drop(columns=["station", "name"], errors="ignore") # Errors="ignore" in case the columns aren't there
#print(weatherData.index.year.value_counts().sort_index())
#plt.plot(weatherData["snow"]) # Plot on graph
#plt.show()

""" ********************************** Machine Learning Part ***************************** """

"""
Get the target data column
"""
# Get the target data column
#weatherData["target"] = weatherData.shift(-1)["tmax"]
weatherData[["maxTemp", "minTemp"]] = weatherData[["tmax", "tmin"]].shift(-1)
#print(weatherData)
weatherData.ffill() # To fill the missing data, with the last row if data is large.

"""
Check for correlation
"""
#print(weatherData.corr())

"""
Initialize ridge regression model, Alpha parameter controls how much the coefficients 
are shrunk to account for collinearity
"""
rr = Ridge(alpha=.1)

#predictors = weatherData.columns[~weatherData.columns.isin(["target", "name", "station"])]
#print(predictors)

#print(getpredictors(weatherData))

#predictions = backtest(weatherData, rr, getpredictors(weatherData))
#print(predictions)

"""
Measure how effective the algorithm was
"""
#print(predictions["diff"].mean())
#print(mean_absolute_error(predictions["actual"], predictions["prediction"]))

rollingHorizon = [3, 14]

for horizon in rollingHorizon:
    for col in ["tmax", "tmin", "prcp"]:
        weatherData = computerolling(weatherData, horizon, col)

#print(weatherData)
weatherData = weatherData.iloc[14:, :] # Remove the first 14 rows since they have NaN
weatherData = weatherData.fillna(0) # Find missing values and fill them in with 0
#print(weatherData)

"""
Go through the data, group it by month, then go one by one through each group and find the mean
of all the date before that given date. Similar to day average.
"""
for col in ["tmax", "tmin", "prcp"]:
    weatherData[f"month_avg_{col}"] = weatherData[col].groupby(weatherData.index.month,
                                                               group_keys=False).apply(expandmean)
    weatherData[f"day_avg_{col}"] = weatherData[col].groupby(weatherData.index.day_of_year,
                                                             group_keys=False).apply(expandmean)
    #print(weatherData)

"""
Final data cleaning.
"""
weatherData.replace([np.inf, -np.inf], np.nan, inplace=True)
weatherData.fillna(0, inplace=True)

"""
Retrain the model with the new data.
"""
#predictors = weatherData.columns[~weatherData.columns.isin(["target", "name", "station"])]
#getpredictors(weatherData)
#print(predictors)
#predictions = backtest(weatherData, rr, getpredictors(weatherData))
#print(predictions["diff"].mean())
#print(mean_absolute_error(predictions["actual"], predictions["prediction"]))
#print(weatherData)

"""Diagnostics"""
#print(predictions.sort_values("diff", ascending= False)) # Get the days which have the biggest errors
#print(weatherData.loc["1990-03-07": "1990-03-14"])
#print(predictions["diff"].round().value_counts().sort_index())
#plt.plot(predictions["diff"].round().value_counts().sort_index() / predictions.shape[0])
#plt.show()
targets = ["maxTemp", "minTemp"]
all_results = []

for target in targets:
    predictions = backtest(weatherData, rr, getpredictors(weatherData), target)
    all_results.append(predictions)

multi_predictions = pd.concat(all_results)
for target in targets:
     print(f"\n==== All Predictions for {target} ====")
     print(multi_predictions[multi_predictions["target"] == target][["actual", "prediction", "diff"]])
#print(predictions)