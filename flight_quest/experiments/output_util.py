import os
import pandas as pd
from flight_quest.io import local_constants
from flight_quest.ml.data_util import Transform
from flight_quest.util import DirForDate, MultiOR, CountNan


def Predict(df, predictor):
  X, _ = Transform([df.last_era_update - df.last_era_update_time], df.actual_runway_arrival - df.last_era_update)
  prediction = predictor.predict(X)
  assert len(prediction) == len(df.last_era_update), (len(prediction), len(df.last_era_update))
  assert CountNan(prediction) == 0
  default_ra = df.scheduled_runway_arrival + df.actual_runway_departure - df.scheduled_runway_departure
  default_ga = df.scheduled_gate_arrival + df.actual_runway_departure - df.scheduled_runway_departure
  df['actual_runway_arrival'] = MultiOR(df.last_era_update + prediction, df.last_era_update, df.last_ega_update, default_ra, df.scheduled_gate_arrival, default_ga)
  df['actual_gate_arrival'] = MultiOR(df.last_ega_update, default_ga, df.scheduled_gate_arrival)
  return df


def PredictAndWriteToFile(fout, predictor, par_dir):
  fpath = os.path.join(par_dir, 'good', 'flighthistory.csv')
  df = pd.read_csv(fpath, index_col='flight_history_id')
  df_pred = Predict(df, predictor)
  test_flights_path = os.path.join(par_dir, 'test_flights.csv')
  df_test_flights = pd.read_csv(test_flights_path, index_col='flight_history_id')
  public_predictions = df_test_flights.join(df_pred, lsuffix='left')
  public_predictions.to_csv(fout, cols=['actual_runway_arrival', 'actual_gate_arrival'],
                            header=False)
  assert CountNan(public_predictions.actual_runway_arrival) == 0
  assert CountNan(public_predictions.actual_gate_arrival) == 0


def GenerateOutputCSV(predictor, fname):
  output_fname = os.path.join(local_constants.OUTPUT_DIR, fname)
  with open(output_fname, 'w') as fout:
    for n in range(26, 31):
      par_dir = os.path.join(DirForDate('2012-11-%02d' % n,
                                        parent_dir=local_constants.LEADERBOARD_DATA_DIR))
      PredictAndWriteToFile(fout, predictor, par_dir)

    for n in range(1, 10):
      par_dir = os.path.join(DirForDate('2012-12-%02d' % n,
                                        parent_dir=local_constants.LEADERBOARD_DATA_DIR))
      PredictAndWriteToFile(fout, predictor, par_dir)