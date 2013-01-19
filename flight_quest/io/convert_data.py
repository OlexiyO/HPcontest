import numpy as np
import os
import shutil
import datetime
import dateutil
import itertools
import pandas as pd
from flight_quest.io import local_constants
from flight_quest.io.parse_METAR import MergeMETARFiles
from flight_quest.util import DateStrToMinutes, RoundSeries, FloorSeries

OUT_DIR = 'good'


def AddLastEstimationTimes(df_main, df_all_estimation, cutoff_series=None):
  df_main['last_era_update'] = df_main.scheduled_runway_arrival
  df_main['last_ega_update'] = df_main.scheduled_gate_arrival
  df_main['last_era_update_time'] = np.nan
  df_main['last_ega_update_time'] = np.nan
  for flight_id, time_recorded, ega, era in itertools.izip(df_all_estimation.flight_history_id,
                                                           df_all_estimation.date_time_recorded,
                                                           df_all_estimation.ega_update,
                                                           df_all_estimation.era_update):
    if ((cutoff_series is not None) and (flight_id in cutoff_series) and
        (time_recorded >= cutoff_series.get_value(flight_id))):
      continue

    # This filters out NANs as well.
    if ega > -1000:
      print flight_id
      print flight_id in df_main.index
      prev_ega_update_time = df_main.last_ega_update_time.get_value(flight_id)
      if np.isnan(prev_ega_update_time) or time_recorded > prev_ega_update_time:
        df_main.last_ega_update_time.set_value(flight_id, time_recorded)
        df_main.last_ega_update.set_value(flight_id, ega)
    if era > -1000:
      prev_era_update_time = df_main.last_era_update_time.get_value(flight_id)
      if np.isnan(prev_era_update_time) or time_recorded > prev_era_update_time:
        df_main.last_era_update_time.set_value(flight_id, time_recorded)
        df_main.last_era_update.set_value(flight_id, era)

  df_main.last_era_update -= 60 * df_main.arrival_airport_timezone_offset * (df_main.last_era_update_time > 0)
  df_main.last_ega_update -= 60 * df_main.arrival_airport_timezone_offset * (df_main.last_ega_update_time > 0)
  df_main['last_era_update_time'] = FloorSeries(df_main.last_era_update_time)
  df_main['last_ega_update_time'] = FloorSeries(df_main.last_ega_update_time)


def TransformWeatherStations():
  # Assuming we are in the root directory with all archives unpacked in subdirs.
  f = pd.read_csv('Reference/weather_stations.csv', delimiter=';')
  f.to_csv('Reference/weather_stations.csv', sep=',', index=False)

MISSING = 'MISSING'


def IsDateValid(s):
  if len(s) != 14:
    return False
  if not (s[2] == '/' and s[5] == '/' and s[8] == ' ' and s[11] == ':'):
    return False
  for i, c in enumerate(s):
    if i not in [2, 5, 8, 11] and not c.isdigit():
      return False
  return True


def ParseDateTime(s, t0_notimezone):
  # s = "11/15/12 18:36"
  if not IsDateValid(s):
    return -1000
  month = int(s[:2])
  day = int(s[3:5])
  year = 2000 + int(s[6:8])
  hour = int(s[9:11])
  minute = int(s[12:])
  t1 = datetime.datetime(year, month, day, hour=hour, minute=minute)
  return (t1 - t0_notimezone).total_seconds() / 60.


def ParseNewEstimationTime(desc, field_name, t0_notimezone):
  # Parses estimation times from a line flight_history_events.csv.
  datetime_len = len('12/04/12 14:44')
  old_prefix = ' Old='
  new_prefix = ' New='
  prefix_len = len(new_prefix)
  n1 = desc.find(field_name)

  if n1 != -1:
    n1 += 4
    if desc[n1:].startswith(old_prefix):
      n1 += (prefix_len + datetime_len)
    if desc[n1:].startswith(new_prefix):
      try:
        return ParseDateTime(desc[n1 + prefix_len:n1 + prefix_len + datetime_len].strip(), t0_notimezone)
      except Exception as e:
        return -1000
  return -1000


def PrettifyFlightEvents(events_in_filepath, events_out_filepath, t0):
  t0_notimezone = t0.replace(tzinfo=None)
  df_events = pd.read_csv(events_in_filepath)
  df_events = df_events[df_events.data_updated.map(lambda x: isinstance(x, basestring))]

  # Save it as float.
  df_events['date_time_recorded'] = df_events.date_time_recorded.map(lambda x: DateStrToMinutes(x, t0))
  # The next two will not include arrival airport offset, because it is inconvenient to read it here.
  df_events['era_update'] = df_events.data_updated.map(lambda desc: ParseNewEstimationTime(desc, 'ERA', t0_notimezone))
  df_events['ega_update'] = df_events.data_updated.map(lambda desc: ParseNewEstimationTime(desc, 'EGA', t0_notimezone))
  df_events = df_events[(df_events.ega_update > -1000) | (df_events.era_update > -1000)]
  df_events['era_update'] = FloorSeries(df_events.era_update.map(lambda x: np.nan if x < -990 else x))
  df_events['ega_update'] = FloorSeries(df_events.ega_update.map(lambda x: np.nan if x < -990 else x))

  df_events.to_csv(events_out_filepath, index=False, cols=['flight_history_id', 'date_time_recorded', 'ega_update', 'era_update'])


def PrettifyFlightHistory(history_infile, fh_events_file, history_outfile, t0):
  df = pd.read_csv(history_infile, index_col='flight_history_id')
  col_names = [
      'published_departure',
      'published_arrival',
      'scheduled_gate_departure',
      'actual_gate_departure',
      'scheduled_gate_arrival',
      'actual_gate_arrival',
      'scheduled_runway_departure',
      'actual_runway_departure',
      'scheduled_runway_arrival',
      'actual_runway_arrival',]

  for name in col_names:
    df[name] = df[name].map(lambda x : DateStrToMinutes(x, t0))

  df_events = pd.read_csv(fh_events_file)
  AddLastEstimationTimes(df, df_events)
  df.to_csv(history_outfile)


def GenerateHelperFeaturesFromHistory(in_filepath, out_filepath):
  df = pd.read_csv(in_filepath)
  df['actual_flight_time'] = df.actual_runway_arrival - df.actual_runway_departure
  df['actual_taxi_departure'] = df.actual_runway_departure - df.actual_gate_departure
  df['actual_taxi_arrival'] = df.actual_gate_arrival - df.actual_runway_arrival

  df['scheduled_flight_time'] = df.scheduled_runway_arrival - df.scheduled_runway_departure
  df['scheduled_taxi_departure'] = df.scheduled_runway_departure - df.scheduled_gate_departure
  df['scheduled_taxi_arrival'] = df.scheduled_gate_arrival - df.scheduled_runway_arrival

  df['runway_delay'] = df.actual_runway_arrival - df.scheduled_runway_arrival
  df['gate_delay'] = df.actual_gate_arrival - df.scheduled_gate_arrival
  df['taxi_arrival_delta'] = df.actual_taxi_arrival - df.scheduled_taxi_arrival
  df['flight_delta'] = df.actual_flight_time - df.scheduled_flight_time

  col_names = ['flight_history_id', 'flight_delta', 'taxi_arrival_delta',
               'actual_flight_time', 'actual_taxi_departure', 'actual_taxi_arrival',
               'scheduled_flight_time', 'scheduled_taxi_departure', 'scheduled_taxi_arrival',
               'runway_delay', 'gate_delay']
  df.to_csv(out_filepath, index=False, cols=col_names)


ShortenFloat = lambda s: '%.2f' % float(s)


def ProcessASDIWayPointFile(in_path, out_path):
  # In 'asdifpwaypoint.csv', first 2 fields are ok; last 2 fields are floats. Shorten them.
  def ShortenLine(line):
    x = line.split(',')
    x[2] = ShortenFloat(x[2])
    x[3] = ShortenFloat(x[3])
    return ','.join(x) + '\n'  # '\n' needed because '\n' in x[3] would be eaten by ShortenFloat.

  with open(in_path) as fin, open(out_path, 'w') as fout:
    fout.write(fin.readline())  # First line is title -- copy with no changes.
    fout.writelines(itertools.imap(ShortenLine, fin))


def ProcessASDIPositionFile(in_path, out_path, t0):
  # In 'asdiposition.csv', first field (no 0) is time -- need to transform it to minutes.
  # Field no 4 and no 5 are coordinates -- need to shorten them.
  def ShortenLine(line):
    x = line.split(',')
    x[0] = '%.2f' % DateStrToMinutes(x[0], t0)
    x[4] = ShortenFloat(x[4])
    x[5] = ShortenFloat(x[5])
    return ','.join(x)

  with open(in_path) as fin, open(out_path, 'w') as fout:
    fout.write(fin.readline())  # First line is title -- copy with no changes.
    fout.writelines(itertools.imap(ShortenLine, fin))


def ProcessASDI(in_dir, out_dir, t0):
  # Files to be copied with no changes.
  no_changes = ['asdiairway.csv', 'asdifpcenter.csv', 'asdifpfix.csv', 'asdifpsector.csv',]
  for filename in no_changes:
    shutil.copy(os.path.join(in_dir, filename), out_dir)

  in_path = os.path.join(in_dir, 'asdifpwaypoint.csv')
  out_path = os.path.join(out_dir, 'asdifpwaypoint.csv')
  ProcessASDIWayPointFile(in_path, out_path)

  in_path = os.path.join(in_dir, 'asdiposition.csv')
  out_path = os.path.join(out_dir, 'asdiposition.csv')
  ProcessASDIPositionFile(in_path, out_path, t0)


def ProcessFlightHistory(base_dir, out_dir, t0):
  """Transforms input files to better format.

  Requires us to 'cd' into parent directory for that date before working.

  Args:
    t0: Midnight UTC for the day we are working with.
  """
  history_infile = os.path.join(base_dir, 'FlightHistory', 'flighthistory.csv')
  events_infile = os.path.join(base_dir, 'FlightHistory', 'flighthistoryevents.csv')

  history_outfile = os.path.join(out_dir, 'flighthistory.csv')
  features_outfile = os.path.join(out_dir, 'history_features.csv')
  events_outfile = os.path.join(out_dir, 'history_event_features.csv')

  #PrettifyFlightEvents(events_infile, events_outfile, t0)
  PrettifyFlightHistory(history_infile, events_outfile, history_outfile, t0)
  #GenerateHelperFeaturesFromHistory(history_outfile, features_outfile)


def RunMe(parent_dir, date_str, output_subdir):
  """Takes raw data for one day and transforms it."""
  t0 = dateutil.parser.parse(date_str).replace(tzinfo=dateutil.tz.tzutc())
  base_dir = os.path.join(parent_dir, date_str.replace('-', '_'))
  asdi_dir =  os.path.join(base_dir, 'ASDI')
  out_dir = os.path.join(base_dir, output_subdir)
  if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
  #ProcessFlightHistory(base_dir, out_dir, t0)
  #ProcessASDI(asdi_dir, out_dir, t0)
  MergeMETARFiles(base_dir, out_dir, t0)
  print 'Done everything for ', date_str


def main():
  date_str = '2012-11-16'
  parent_dir = local_constants.PARENT_DATA_DIR
  RunMe(parent_dir, date_str, 'good')
  return
  for x in range(26, 31):
    date_str = '2012-11-%s' % x
    parent_dir = local_constants.LEADERBOARD_DATA_DIR
    RunMe(parent_dir, date_str, 'good')
    print 'Merged for', date_str

  for x in range(12, 26):
    date_str = '2012-11-%s' % x
    parent_dir = local_constants.PARENT_DATA_DIR
    RunMe(parent_dir, date_str, 'good')
    print 'Merged for', date_str

  for x in range(1, 10):
    date_str = '2012-12-%02d' % x
    parent_dir = local_constants.LEADERBOARD_DATA_DIR
    RunMe(parent_dir, date_str, 'good')
    print 'Merged for', date_str


if __name__ == "__main__":
  main()
