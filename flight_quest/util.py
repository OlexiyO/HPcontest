import math
import os
import dateutil
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from flight_quest.io import local_constants

def DateToMinutes(date, initial_date):
  return date - initial_date if isinstance(date, pd.lib.Timestamp) else -1000


def RMSE(df, name1, name2):
  filtered = df[df[name1] + df[name2] > 0]
  total = np.mean(np.power(filtered[name1] - filtered[name2], 2))
  return math.sqrt(total)


def RMSE2(ser1, ser2):
  return math.sqrt(np.mean(np.power(ser1 - ser2, 2)))


def Plot(x, ys, style='.', line=None):
  colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
  Y = [ys] if isinstance(ys, pd.Series) else ys
  plt.cla()
  for y, color in zip(Y, colors):
    plt.plot(x, y, '%s%s' % (color, style))
  if line is not None:
    plt.plot(x, Y[0].map(lambda x: line), 'k-')
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
    return ''


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
  return a.combine(b, lambda x, y: x if np.isnan(y) else np.nan)
