import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


Months = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
  ]
Weekdays = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
  ]


def is_usable(criterion, temp, humidity, precipitation, windspeed, winddir):
  """
  function: is_usable
  Determines if certain weather conditions meet a usable criterion.

  Arguments:
    - criterion (dict): the dictionary of values to use as criterion
    - temp (float): the temperature in Celsius
    - humidity (float): the humidity as a decimal [0..1]
    - precipitation (float): the amount of precipitation in m
    - windspeed (float): the windspeed in m/s
    - winddir (float): the direction of the wind, measured from North
  Returns:
    true iff the weather conditions permit use, false otherwise
  """
  wind_projection = windspeed * np.cos((winddir - criterion['FACING'] - 180) * np.pi / 180)
  return (criterion['MIN_TEMP'] <= temp <= criterion['MAX_TEMP'] and
          criterion['MIN_HUMIDITY'] <= humidity <= criterion['MAX_HUMIDITY'] and
          wind_projection <= criterion['MAX_WINDSPEED'] and
          precipitation <= criterion['MAX_PRECIPITATION'])


def usable_days(criterion, df):
  """

  Arguments:
    criterion (dict): the criterion to evaluate whether an entry classifies as usable
    df (DataFrame): the DataFrame containing the weather data
  Returns:
    df (DataFrame): A new DataFrame with added columns for Gregorian month, and whether or not the day is usable
  """
  usable = [
    is_usable(criterion,
              df.loc[date, 'temp'],
              df.loc[date, 'humidity'],
              df.loc[date, 'precipitation'],
              df.loc[date, 'windspeed'],
              df.loc[date, 'winddir'])
    for date in df.index
  ]
  months = [
    date.month for date in df.index
    ]
  weekdays = [
    date.isoweekday() for date in df.index
    ]
  return df.assign(month = months, isusable = usable, weekday = weekdays)


def expectations(df):
  """
  function: expectations
  Averages the expected values by month

  Arguments:
    df (DataFrame): the DataFrame containing the weather data
  Returns:
    df (DataFrame): a new DataFrame with the averaged data
  """
  data = []
  for month in range(12):
    entry = dict()
    sf = df[df['month'] == month + 1]
    for column, series in sf.iteritems():
      entry[column] = np.mean(series)
    entry['month'] = Months[month]
    data.append(entry)
  return pd.DataFrame(data).set_index('month').drop(columns = ['weekday'])


def make_figures(df):
  fig, axs = plt.subplots(6, figsize = (10, 10))
  xs = [month[:3] for month in df.index]
  [temps, humidities, usability, precipitations, pressures, winds] = axs
  temps.bar(xs, 32 + df['temp'] * (9/5), label='Average Temp (F)')
  temps.bar(xs, 32 + df['feelslike'] * (9/5), label='Average Adjusted Temp (F)')
  humidities.bar(xs, df['humidity'], label='Averaged Humidity (%)')
  usability.bar(xs, df['isusable'], label='Average Usability (%)')
  precipitations.bar(xs, df['precipitation'], label='Average Precipitation (mm)')
  pressures.bar(xs, df['pressure'], label='Average pressure (Hg)')
  winds.bar(xs, 0.44704*df['windspeed'], label='Average Wind Speed (Mph)')
  for ax in axs:
    ax.legend(loc = 'best', bbox_to_anchor = (0.5, 1.05),
              ncol = 3, fancybox = True, shadow = True)
  fig.tight_layout()
  fig.savefig('HudsonYardsWeatherData.png', dpi = 500)
  plt.show()

