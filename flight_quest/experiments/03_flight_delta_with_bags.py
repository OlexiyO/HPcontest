'''
We learn a GradientBoost model with
  input = last_era_update - last_era_update_time
  golden = actual_runway_arrival - last_era_update
  prediction = last_era_update + model
'''
import os
import pandas as pd
from flight_quest import util
from flight_quest.experiments import output_util
from flight_quest.io import local_constants
from flight_quest.ml import gradient_booster, base_predictor
from flight_quest.ml.base_predictor import PostProcessedPredictor
from flight_quest.ml.cv_util import PredictRunwayRMSE
from flight_quest.ml.data_util import Transform
from flight_quest.ml.gradient_booster import MergeDFs
from flight_quest.util import DirForDate


def _TrainModel(MODEL_NAME):
  DF_train = []
  # Test setting here
  for n in range(13, 26):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF_train.append(pd.read_csv(fpath, index_col='flight_history_id'))

  DF_test = []
  for n in range(26, 30):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR), 'model', 'training.csv')
    DF_test.append(pd.read_csv(fpath, index_col='flight_history_id'))
  for n in range(1, 10):
    fpath = os.path.join(DirForDate('2012-12-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR), 'model', 'training.csv')
    DF_test.append(pd.read_csv(fpath, index_col='flight_history_id'))

  input_func = lambda df: [(df.last_era_update - df.last_era_update_time)]
  output_func = lambda df: (df.actual_runway_arrival - df.last_era_update)
  training_filter = lambda df: (df.actual_runway_arrival < df.actual_gate_arrival)
  fname = os.path.join(local_constants.OUTPUT_DIR, '%s.model' % MODEL_NAME)

  param_overrides = {'n_estimators': 1000, 'min_samples_leaf': 5, 'learn_rate': .05}

  merged_df = MergeDFs(DF_train)
  merged_test = MergeDFs(DF_test[:5])
  predictor, score = gradient_booster.TrainWithOOB(
      merged_df, merged_test, input_func, output_func, param_overrides, training_filter=training_filter,
      num_bags=20, bag_mods=10)
  return predictor, score


def PrintRMSEs(predictor):
  DF = []
  for n in range(13, 26):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n), 'model', 'training.csv')
    DF.append(pd.read_csv(fpath, index_col='flight_history_id'))

  DF_test = []
  for n in range(26, 30):
    fpath = os.path.join(DirForDate('2012-11-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR), 'model', 'training.csv')
    DF_test.append(pd.read_csv(fpath, index_col='flight_history_id'))
  for n in range(1, 10):
    fpath = os.path.join(DirForDate('2012-12-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR), 'model', 'training.csv')
    DF_test.append(pd.read_csv(fpath, index_col='flight_history_id'))

  input_func = lambda df: [(df.last_era_update - df.last_era_update_time)]
  PredictRunwayRMSE(DF, predictor, input_func, 'TrainOnSeriesOfDF')
  PredictRunwayRMSE(DF_test, predictor, input_func, 'Test')


def PlotPredictor(predictor):
  fpath = os.path.join(DirForDate('2012-11-%02d' % 22), 'model', 'training.csv')
  df = pd.read_csv(fpath, index_col='flight_history_id')
  X, _ = Transform([df.last_era_update - df.last_era_update_time], df.actual_runway_arrival - df.last_era_update)
  prediction = predictor.predict(X)
  assert len(prediction) == len(df.last_era_update), (len(prediction), len(df.last_era_update))
  util.Plot(X, [prediction])


def main():
  MODEL_NAME = 'model_03_20'
  # Uncomment this to train model from scratch.
  fname = os.path.join(local_constants.OUTPUT_DIR, MODEL_NAME)
  predictor, score = _TrainModel(MODEL_NAME)
  predictor.Save(fname)
  #predictor = base_predictor.LoadPredictor(fname)
  PlotPredictor(predictor)
  PrintRMSEs(predictor)
  output_util.GenerateOutputCSV(predictor, '%s.output' % MODEL_NAME)


if __name__ == "__main__":
  main()
