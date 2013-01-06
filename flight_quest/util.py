import math
import os
import dateutil
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from flight_quest.io import local_constants

def DateToMinutes(date, initial_date):
  return date - initial_date if isinstance(date, pd.lib.Timestamp) else -1000


def RMSE(ser1, ser2):
  assert len(ser1) == len(ser2)
  assert all((np.isnan(b) or not np.isnan(a)) for a, b in zip(ser1, ser2))
  return math.sqrt(np.mean(np.power(ser1 - ser2, 2)))


def Plot(x, ys, style='.', line=None, filter=None):
  filtered_x = x[filter] if (filter is not None) else x
  colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']
  Y = [ys] if isinstance(ys, pd.Series) else ys
  Y = [y[filter] for y in Y] if (filter is not None) else Y
  plt.cla()
  for y, color in zip(Y, colors):
    plt.plot(filtered_x, y, '%s%s' % (color, style))
  if line is not None:
    try:
      for l in line:
        plt.plot(filtered_x, Y[0].map(lambda x: l), 'k-')
    except TypeError:
      plt.plot(filtered_x, Y[0].map(lambda x: line), 'k-')
  plt.show()


def DirForDate(date_str, parent_dir=local_constants.PARENT_DATA_DIR):
  return os.path.join(parent_dir, date_str.replace('-', '_'))


def DateStrToMinutes(s, t0):
  if not s:
    return s
  try:
    t1 = dateutil.parser.parse(s)
    return (t1 - t0).total_seconds() / 60.
  except ValueError:
    return np.nan


def LoadForDay(date_str, parent_dir=local_constants.PARENT_DATA_DIR):
  dir = DirForDate(date_str, parent_dir=parent_dir)
  history_path = os.path.join(dir, 'good/flighthistory.csv')
  features_path = os.path.join(dir, 'good/history_features.csv')
  idf = pd.read_csv(history_path)
  ndf = pd.read_csv(features_path)
  return idf.merge(ndf, on='flight_history_id')


def LoadAllTraining():
  DF = []
  for n in range(12, 26):
    DF.append(LoadForDay('2012-11-%d' % n, parent_dir=local_constants.PARENT_DATA_DIR))
  return DF


def LoadAllPublicLeaderboard():
  DF = []
  for n in range(26, 31):
    DF.append(LoadForDay('2012-11-%d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR))
  for n in range(1, 10):
    DF.append(LoadForDay('2012-12-%2d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR))
  return DF


def OR(a, b):
  return a.combine(b, lambda x, y: y if np.isnan(x) else x)


def AND(a, b):
  return a.combine(b, lambda x, y: x if not np.isnan(y) else np.nan)


def MultiOR(a, *args):
  r = a
  for b in args:
    r = r.combine(b, lambda x, y: y if np.isnan(x) else x)
  return r


def CountNan(x):
  return len([y for y in x if np.isnan(y)])


def FloorSeries(series):
  # Debug: this won't change type to int if series has missing data.
  return pd.Series(series.map(int, na_action='ignore'), dtype=np.int)


def RoundSeries(series):
  # Debug: this won't change type to int if series has missing data.
  R = lambda x: int(x + .5)
  return pd.Series(series.map(R, na_action='ignore'), dtype=np.int)
