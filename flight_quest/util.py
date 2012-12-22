import math
import os
import dateutil
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from flight_quest.io.local_constants import PARENT_DATA_DIR

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


def DirForDate(date_str):
  return os.path.join(PARENT_DATA_DIR, date_str.replace('-', '_'))


def DateStrToMinutes(s, t0):
  if not s:
    return s
  try:
    t1 = dateutil.parser.parse(s.replace('_', '-'))
    return (t1 - t0).total_seconds() / 60.
  except ValueError:
    return ''
