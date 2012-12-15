import os
import shutil
import dateutil
import pandas as pd
from flight_quest.io.parse_METAR import   MergeMETARFiles
from flight_quest.util import DateStrToMinutes


OUT_DIR = 'good'


def TransformWeatherStations():
  # Assuming we are in the root directory with all archives unpacked in subdirs.
  f = pd.read_csv('Reference/weather_stations.csv', delimiter=';')
  f.to_csv('Reference/weather_stations.csv', sep=',', index=False)

MISSING = 'MISSING'


def PrettifyFlightEvents(in_filepath, out_filepath, t0):
  col_names = ['date_time_recorded']
  _PrettifyTimesInFile(in_filepath, out_filepath, t0, col_names)


def PrettifyFlightHistory(in_filepath, out_filepath, t0):
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
  _PrettifyTimesInFile(in_filepath, out_filepath, t0, col_names)


def _PrettifyTimesInFile(in_filepath, out_filepath, t0, col_names):
  df = pd.read_csv(in_filepath)
  for name in col_names:
    df[name] = df[name].map(lambda x : DateStrToMinutes(x, t0))
  df.to_csv(out_filepath, index=False)


def GenerateHelperFeaturesFromHistory(in_filepath, out_filepath):
  df = pd.read_csv(in_filepath)
  df['actual_flight_time'] = df.actual_runway_arrival - df.actual_runway_departure
  df['actual_taxi_departure'] = df.actual_runway_departure - df.actual_gate_departure
  df['actual_taxi_arrival'] = df.actual_gate_arrival - df.actual_runway_arrival

  df['scheduled_flight_time'] = df.scheduled_runway_arrival - df.scheduled_runway_departure
  df['scheduled_taxi_departure'] = df.scheduled_runway_departure - df.scheduled_gate_departure
  df['scheduled_taxi_arrival'] = df.scheduled_gate_arrival - df.scheduled_runway_arrival

  df['flight_delta'] = df['actual_flight_time'] - df['scheduled_flight_time']
  df['taxi_arrival_delta'] = df.actual_taxi_arrival - df.scheduled_taxi_arrival

  col_names = ['flight_history_id', 'flight_delta', 'taxi_arrival_delta',
               'actual_flight_time', 'actual_taxi_departure', 'actual_taxi_arrival',
               'scheduled_flight_time', 'scheduled_taxi_departure', 'scheduled_taxi_arrival',]
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
    fout.writelines(map(ShortenLine, fin))


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
    fout.writelines(map(ShortenLine, fin))


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
  history_outfile = os.path.join(out_dir, 'flighthistory.csv')
  events_outfile = os.path.join(out_dir, 'flighthistoryevents.csv')
  features_outfile = os.path.join(out_dir, 'history_features.csv')
  history_infile = os.path.join(base_dir, 'FlightHistory', 'flighthistory.csv')
  events_infile = os.path.join(base_dir, 'FlightHistory', 'flighthistoryevents.csv')
  PrettifyFlightHistory(history_infile, history_outfile, t0)
  PrettifyFlightEvents(events_infile, events_outfile, t0)
  GenerateHelperFeaturesFromHistory(history_outfile, features_outfile)


def RunMe(date_str):
  t0 = dateutil.parser.parse(date_str).replace(tzinfo=dateutil.tz.tzutc())
  base_dir = 'C:\\Dev\\Kaggle\\FlightQuest\\InitialTrainingSet\\%s' % date_str.replace('-', '_')
  asdi_dir =  os.path.join(base_dir, 'ASDI')
  out_dir = os.path.join(base_dir, 'good')
  if not os.path.exists(out_dir):
    os.mkdir(out_dir)
  ProcessFlightHistory(base_dir, out_dir, t0)
  ProcessASDI(asdi_dir, out_dir, t0)
  MergeMETARFiles(date_str)
  print 'Done everything for ', date_str


def CheckFieldUnique(filepath, other_path, field_name):
  df = pd.read_csv(filepath)
  other_df = pd.read_csv(other_path)
  dd = df[field_name].to_dict()
  x = sorted((v, k) for k, v in dd.iteritems())
  for i, y in enumerate(x):
    if i > 0 and x[i - 1][0] == y[0]:
      #print filepath, y
      #lst = other_df.weather_station_code[(other_df.metar_reports_id == y)].tolist()
      #assert len(lst) == 1
      #yield lst[0]
      print df.values[x[i - 1][1]]
      print df.values[y[1]]
      print ''


for x in range(12, 26):
  date_str = '2012-11-%s' % x
  MergeMETARFiles(date_str)
  print 'Merged for', date_str