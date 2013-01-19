import os
import dateutil
import pandas as pd
import numpy as np
from flight_quest import util


"""This module parses data in metar directory.

Also, drops duplicates for some tables, drops some fields and converts time --> minutes.
"""

ID_FIELD = 'metar_reports_id'


def Cumulus(desc):
  """Bigger value means better conditions."""
  if 'cumulus' in desc:
    return 1
  elif 'cumuloninbus' in desc:
    return 0
  else:
    return 2


def GetHeight(desc):
  """Bigger height means better conditions."""
  in1 = desc.find('at ')
  in2 = desc.find(' feet')
  return int(desc[in1 + 3:in2]) if in1 >= 0 and in2 >= 0 else 1000000


# Later entries mean better conditions
CLOUD_TYPES = [
  (0, 'vertical visibility'),
  (1, 'overcast layer'),
  (2, 'broken layer'),
  (3, 'scattered layer'),
  (4, 'few clouds'),
  (5, 'clear'),]


def GetCloudsType(desc):
  for ind, ct in CLOUD_TYPES:
    if desc.startswith(ct):
      return (2 * ind)
  print 'Unknown cloud type', desc
  assert False


def ParseSkys(sky_filepath):
  sky_df = pd.read_csv(sky_filepath)

  # TODO: Finish this
  # Parse METAR properly

  data = []
  prev = {}
  for row in sky_df.values:
    metar_id = row[1]
    desc = row[2].lower()
    new_data = [metar_id, GetCloudsType(desc), GetHeight(desc), Cumulus(desc)]
    next_ind = len(data)
    ind = prev.get(metar_id, -1)
    if ind != -1:
      # Take max cumulus
      data[ind][3] = max(data[ind][3], new_data[3])
      if data[ind][2] < new_data[2]:
        # Take lower layer of clouds + 1
        data[ind][2] = new_data[2] - 1
        data[ind][1] = new_data[1]
      else:
        data[ind][2] -= 1
    else:
      prev[metar_id] = next_ind
      data.append(new_data)
  return data


def ProcessSky(sky_filepath):
  sky_2d_array = ParseSkys(sky_filepath)
  return pd.DataFrame(sky_2d_array, columns=[ID_FIELD, 'clouds_type', 'clouds_height', 'cumulus'])


def ParseWindDirectionDelta(s):
  # Each string is formatted as
  # "Wind variable from XXX degrees to YYY degrees"
  #if not isinstance(s, basestring):
  #  return 0
  in1 = s.index('from ') + 5
  in2 = s.index(' degrees')
  in3 = s.index('to ') + 3
  in4 = s.index(' degrees', in2 + 8)
  assert in2 - in1 == 3, s
  assert in4 - in3 == 3, s
  return (360 + int(s[in3:in4]) - int(s[in1:in2])) % 360


def ProcessReportsCombined(ID_FIELD, main_filepath, t0):
  main_df = pd.read_csv(main_filepath, index_col=ID_FIELD)
  main_df['time'] = main_df['date_time_issued'].map(lambda x: util.DateStrToMinutes(x, t0), na_action='ignore')
  main_df['is_wind_variable'] = main_df['is_wind_direction_variable'].map(lambda x: 1 if x == 'T' else 0, na_action='ignore')
  main_df['wind_direction_delta'] = main_df['variable_wind_direction'].map(ParseWindDirectionDelta, na_action='ignore')
  useful_cols = [ID_FIELD, 'weather_station_code', 'time', 'is_wind_variable', 'wind_gusts',
                 'wind_speed', 'wind_direction_delta', 'visibility', 'temperature', 'dewpoint',
                 'altimeter', 'sea_level_pressure']
  return main_df[useful_cols]


def ProcessRunway(ID_FIELD, runway_filepath):
  runway_df = pd.read_csv(runway_filepath)
  return runway_df.drop_duplicates(cols=[ID_FIELD])[[ID_FIELD, 'min_visible', 'max_visible']]


def MergeMETARFiles(base_dir, output_dir, t0):
  input_dir = os.path.join(base_dir, 'metar')
  sky_filepath = os.path.join(input_dir, 'flightstats_metarskyconditions_combined.csv')
  runway_filepath = os.path.join(input_dir, 'flightstats_metarrunwaygroups_combined.csv')
  main_filepath = os.path.join(input_dir, 'flightstats_metarreports_combined.csv')

  main_df = ProcessReportsCombined(ID_FIELD, main_filepath, t0)
  #runway_df = ProcessRunway(ID_FIELD, runway_filepath)
  sky_df = ProcessSky(sky_filepath)

  #main_df = main_df.merge(runway_df)
  main_df = main_df.merge(sky_df, on=ID_FIELD)
  main_df.to_csv(os.path.join(output_dir, 'metar_weather.csv'), index=False)
  print 'Converted METAR files for %s' % base_dir