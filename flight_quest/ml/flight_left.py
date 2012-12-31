import cPickle as pickle
import os
import pandas as pd
import numpy as np
from sklearn import ensemble
from sklearn import metrics
from flight_quest import util
from flight_quest.io import local_constants
from flight_quest.ml.gradient_booster import LearnGradientBoost, PrepareForTraining, PrintCVTable, Transform
from flight_quest.util import DirForDate


def LearnOne():
  #filter = OR(OR(df.actual_runway_arrival, df.actual_runway_departure), OR(df.actual_gate_arrival, df.actual_gate_departure))
  fpath = os.path.join(DirForDate('2012-11-15'), 'model', 'training.csv')

  df = pd.read_csv(fpath, index_col='flight_history_id')
  input = df.last_era_update - df.last_era_update_time
  golden = df.last_era_update - df.actual_runway_arrival
  func = LearnGradientBoost([input], golden,
                            param_overrides={'n_estimators': 200}, test_ratio=.2)

  X, y = PrepareForTraining([df.last_era_update - df.last_era_update_time], df.actual_runway_arrival)
  print util.RMSE(df.actual_runway_arrival, df.last_era_update)
  print util.RMSE(df.actual_runway_arrival, df.last_era_update - func.predict(X))


def CrossValidation():
  DF = []
  for n in range(13, 21):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))
  get_input_func = lambda df: [df.last_era_update - df.last_era_update_time]
  get_output_func = lambda df: df.actual_runway_arrival - df.last_era_update
  PrintCVTable(DF, get_input_func, get_output_func, 150)



def DoTraining():
  funcs = []
  DF = []
  for n in range(13, 21):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  get_input_func = lambda df: [df.last_era_update - df.last_era_update_time]
  get_output_func = lambda df: df.actual_runway_arrival - df.last_era_update

  for df in DF:
    funcs.append(LearnGradientBoost(
      get_input_func(df), get_output_func(df),
      param_overrides={'n_estimators': 150}, test_ratio=.01))  # Change 1250 --> 250 --> 150 --> 5

  with open(os.path.join(local_constants.OUTPUT_DIR, 'models1'), 'w') as fout:
    pickle.dump(funcs, fout)

  PredictRMSE(DF, funcs)


def CountNan(x):
  return len([y for y in x if np.isnan(y)])


def PredictRMSE(DF, funcs):
  def F(df):
    return df.last_era_update - df.last_era_update_time
  get_input_func = lambda df: [F(df)]
  get_output_func = lambda df: df.actual_runway_arrival - df.last_era_update

  for df in DF:
    X, y = Transform(get_input_func(df), get_output_func(df))
    prediction = y * 0
    for f in funcs:
      prediction += f.predict(X)
    prediction /= len(funcs)
    assert len(prediction) == len(df.last_era_update), (len(prediction), len(df.last_era_update))
    filter_runway = abs(df.actual_runway_arrival - df.last_era_update) >= -1
    golden_runway = util.AND(df.actual_runway_arrival, df.last_era_update)[filter_runway]
    r1 = util.RMSE(golden_runway, df.last_era_update[filter_runway])
    r2 = util.RMSE(golden_runway, (df.last_era_update + prediction)[filter_runway])
    print 'Runway:', r1 - r2
    util.Plot(df.last_era_update - df.last_era_update_time, [prediction], filter=filter_runway)

    assert len(prediction) == len(df.last_ega_update), (len(prediction), len(df.last_ega_update))
    filter_gate = abs(df.actual_gate_arrival - df.last_ega_update) >= -1
    golden_gate = util.AND(df.actual_gate_arrival, df.last_ega_update)[filter_gate]
    g1 = util.RMSE(golden_gate, df.last_ega_update[filter_gate])
    g2 = util.RMSE(golden_gate, (df.last_ega_update + prediction / 2)[filter_gate])
    print 'Gate:', g1 - g2
    print ''


'''
  TODO:
    * Generate solution and submit it
    * Cut at the best step
    * Submit again.
  '''


def main():
  DF = []
  for n in range(24, 25):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  with open(os.path.join(local_constants.OUTPUT_DIR, 'models1')) as fin:
    funcs = pickle.load(fin)
    PredictRMSE(DF, funcs)


if __name__ == "__main__":
  main()
