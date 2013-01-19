from sklearn import metrics
from flight_quest import util
from flight_quest.ml.data_util import Transform


def PrintCVTable(DF, get_input_func, get_output_func, funcs):
  """For each of data frames, trains a function on it and estimates how good is it on other data frames."""
  ND = len(DF)
  NF = len(funcs)
  data = [([0] * ND) for _ in range(NF + 2)]
  for n, df in enumerate(DF):
    X, y = Transform(get_input_func(df), get_output_func(df))
    P = y * 0
    OOB = y * 0
    for m, f in enumerate(funcs):
      p1 = f.predict(X)
      data[m][n] = metrics.mean_squared_error(p1, y)
      P += p1
      if m != n:
        OOB += p1
    data[NF][n] = metrics.mean_squared_error(P / NF, y)
    # If we provide 3 funcs and 5 DataFrame, we think that functions were trained on the first 3 DFs.
    # Therefore, all funcs are OOB for the last 2 DataFrames.
    oob_funcs = NF - 1 if n < NF else NF
    data[NF + 1][n] = metrics.mean_squared_error(OOB / oob_funcs, y)

  for i, d in enumerate(data):
    print i + 13 if i < NF else ('AV' if i == NF else 'OOB'), ['%.1f' % x for x in d]


def PredictRunwayRMSE(DF, predictor, input_func, name=None):
  """Given list of data frames, computes wins against "last public estimation" benchmark.

  Args:
    DF: List of pd.DataFrame.
    predictor:
    input_func: Function, which takes a pd.DataFrame and returns a list of pd.Series,
        which will be used as input to ML training.
    name: Just prints this name
  """
  if name:
    print 'Predicted win for %s:' % name
  weighted1 = 0
  weighted2 = 0
  total_weight = 0
  for df in DF:
    series_in = input_func(df)
    assert all(len(s) == len(series_in[0]) for s in series_in)
    X, _ = Transform(series_in, [])
    df['prediction'] = predictor.predict(X)
    assert len(df.prediction) == len(series_in[0]), (len(df.prediction), len(series_in[0]))

    filter_runway = (df.actual_runway_arrival < df.actual_gate_arrival)
    golden_runway = df.actual_runway_arrival[filter_runway]
    r1 = util.RMSE(golden_runway, df.last_era_update[filter_runway])
    r2 = util.RMSE(golden_runway, (df.last_era_update + df.prediction)[filter_runway])
    w = len(df.last_era_update[filter_runway])
    weighted1 += r1 * w
    weighted2 += r2 * w
    total_weight += w
    #print 'Runway: %.2f' % (r1 - r2)

  weighted_score = ((weighted1 - weighted2) / total_weight)
  print 'Weighted: %.4f' % weighted_score
  return weighted_score