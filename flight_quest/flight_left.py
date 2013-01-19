import cPickle as pickle
import os
import pandas as pd
from flight_quest.io import local_constants
from flight_quest.ml import cv_util, base_predictor
from flight_quest.ml.gradient_booster import LearnGradientBoostInTwoHalves
from flight_quest.util import DirForDate

# This module contains experiments related to "flight_left" --> "change in estimation" model.

def CrossValidation(funcs_filepath):
  DF = []
  for n in range(13, 21):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  get_input_func = lambda df: [(df.last_era_update - df.last_era_update_time)[df.actual_runway_arrival < df.actual_gate_arrival]]
  get_output_func = lambda df: (df.actual_runway_arrival - df.last_era_update)[df.actual_runway_arrival < df.actual_gate_arrival]

  if funcs_filepath and os.path.exists(funcs_filepath):
    os.path.join(local_constants.TMP_DIR, 'cv_funcs')
    with open(funcs_filepath) as fin:
      funcs = pickle.load(fin)
  else:
    funcs = []
    for df in DF:
      funcs.append(LearnGradientBoostInTwoHalves(
        get_input_func(df), get_output_func(df),
        param_overrides={'n_estimators': 1250}))
    with open(funcs_filepath, 'w') as fout:
      pickle.dump(funcs, fout)

  cv_util.PrintCVTable(DF, get_input_func, get_output_func, funcs)


def main():
  DF = []
  for n in range(13, 22):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  input_func = lambda df: [(df.last_era_update - df.last_era_update_time)]
  output_func = lambda df: (df.actual_runway_arrival - df.last_era_update)
  training_filter = lambda df: (df.actual_runway_arrival < df.actual_gate_arrival)
  fname = os.path.join(local_constants.TMP_DIR, 'models2')

  #CrossValidation()
  # gradient_booster.TrainOnSeriesOfDF(DF, input_func, output_func, training_filter=training_filter, fname=fname)
  #return
  DF = []
  for n in range(22, 26):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  predictor = base_predictor.LoadPredictor(fname)
  cv_util.PredictRunwayRMSE(DF, predictor, input_func)


if __name__ == "__main__":
  main()

