import math
import numpy as np
import pandas as pd

def DateToMinutes(date, initial_date):
  return date - initial_date if isinstance(date, pd.lib.Timestamp) else -1000


def RMSE(df, name1, name2):
  filtered = df[df[name1] + df[name2] > 0]
  total = np.mean(np.power(filtered[name1] - filtered[name2], 2))
  return math.sqrt(total)
