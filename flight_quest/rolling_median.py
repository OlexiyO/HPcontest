from pandas.stats.moments import rolling_median
from flight_quest import util

def PlotRollingMedian(df, field, sort_by, window, min_periods):
  df1 = df.sort_index(by=sort_by)
  rm = rolling_median(df1[field], window, min_periods=min_periods)
  util.Plot(df1[sort_by], rm, line=0)