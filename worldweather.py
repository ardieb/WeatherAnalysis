import requests
import pandas as pd

from datetime import datetime, timedelta
import calendar

from consts import WORLD_WEATHER_ONLINE_API, API_KEY


def last_day_of_month(date):
  return calendar.monthrange(date.year, date.month)[1]


def collect_data_at_coords(lat, long, since = None):
  """
  function: collect_data_at_coords
  Gets weather data by latitude, longitude coordinates

  Arguments:
    - lat (float): the lat in degrees
    - long (float): the long in degrees
    - since (datetime): timestamp to read data since, defaults to 5 years prior
  Returns:
    - data (DataFrame): a dataframe with all weather data
  """
  if not since:
    since = datetime.now() - timedelta(weeks = 52 * 5) # 5 years back
  now = datetime.now()
  data = []
  while since < now:
    to = min(
      datetime(year = since.year, month = since.month, day = last_day_of_month(since)),
      now
      )
    resp = requests.get(WORLD_WEATHER_ONLINE_API, params = dict(
      q = (lat, long),
      key = API_KEY,
      date = since.isoformat(),
      enddate = to,
      format = 'json',
      tp = 12,
      extra = dict(isDayTime = 'yes')
      ))
    resp.raise_for_status()
    data += [
      dict(
        date = datetime.fromisoformat(entry['date']),
        temp = float(entry['hourly'][0]['tempC']),
        feelslike = float(entry['hourly'][0]['FeelsLikeC']),
        windspeed = float(entry['hourly'][0]['windspeedKmph']) * 0.277778,
        winddir = int(entry['hourly'][0]['winddirDegree']),
        precipitation = float(entry['hourly'][0]['precipMM']),
        humidity = float(entry['hourly'][0]['humidity']) / 100,
        pressure = float(entry['hourly'][0]['pressure']),
        ) for entry in resp.json()['data']['weather']]
    since = to + timedelta(days = 1)

  return pd.DataFrame(data).set_index('date')


