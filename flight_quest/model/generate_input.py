import os
import pandas as pd
import numpy as np

from flight_quest.io import local_constants
from flight_quest.io.convert_data import AddLastEstimationTimes


def GenerateWeatherPerFlight(df_joined, df_weather, output_file):
  # TODO(generate this for leaderboard data as well
  """Given cutoff points for flights, find latest available weather info for arrival airport.

  Args:
    df_joined: pd.DataFrame, As built in GenerateOneDay.
    df_weather: pd.DataFrame, as read from metar_weather.csv.
    output_file: string.
  """
  def GetAirportCode(station_code):
    assert len(station_code) == 4, station_code
    return station_code[1:] if station_code.startswith('K') else np.nan

  df_weather['airport_code'] = df_weather.weather_station_code.map(
      GetAirportCode, na_action='ignore')


def GenerateOneDay(parent_dir, date_str):
  input_dir = os.path.join(parent_dir, date_str.replace('-', '_'), 'good')
  output_dir = os.path.join(parent_dir, date_str.replace('-', '_'), 'model')

  if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

  df_flights = pd.read_csv(os.path.join(input_dir, 'flighthistory.csv'), index_col='flight_history_id')
  df_features = pd.read_csv(os.path.join(input_dir, 'history_features.csv'), index_col='flight_history_id')

  df_joined = df_flights.join(df_features)
  # Some data entries have NaN, few have <0 (?). Filter them out.
  df_joined = df_joined[df_joined.actual_flight_time > 0]
  # Relative moment since departure.
  df_joined['cutoff_delta'] = df_joined.actual_flight_time.map(np.random.randint)
  # Absolute timestamp.
  df_joined['cutoff_time'] = df_joined.actual_runway_departure + df_joined.cutoff_delta

  df_events = pd.read_csv(os.path.join(input_dir, 'history_event_features.csv'))
  AddLastEstimationTimes(df_joined, df_events, cutoff_series=df_joined.cutoff_time)
  flight_fields = ['scheduled_flight_time',
                   'scheduled_runway_arrival',
                   'scheduled_gate_arrival',
                   'actual_runway_departure',
                   'actual_runway_arrival',
                   'actual_gate_arrival',
                   'cutoff_delta',
                   'cutoff_time',
                   'last_era_update',
                   'last_ega_update',
                   'last_era_update_time',
                   'last_ega_update_time']
  df_joined.to_csv(os.path.join(output_dir, 'training.csv'), cols=flight_fields)

  metar_file = os.path.join(input_dir, 'metar_weather.csv')
  df_weather = pd.read_csv(metar_file, index_col='metar_reports_id')
  output_file = os.path.join(output_dir, 'per_flight_weather.csv')
  GenerateWeatherPerFlight(df_joined, df_weather, output_file)


def main():
  GenerateOneDay(local_constants.PARENT_DATA_DIR, '2012-11-%02d' % 13)
  return
  for n in range(12, 26):
    GenerateOneDay(local_constants.PARENT_DATA_DIR, '2012-11-%02d' % n)

  for n in range(26, 31):
    GenerateOneDay(local_constants.LEADERBOARD_DATA_DIR, '2012-11-%02d' % n)

  for n in range(1, 10):
    GenerateOneDay(local_constants.LEADERBOARD_DATA_DIR, '2012-12-%02d' % n)


if __name__ == '__main__':
  main()
