'''
We learnt a GradientBoost model with
  input = last_era_update - last_era_update_time
  golden = actual_runway_arrival - last_era_update
'''
import cPickle as pickle
import os
import pandas as pd
from flight_quest.io import local_constants
from flight_quest.ml.flight_left import CountNan
from flight_quest.ml.gradient_booster import Transform
from flight_quest.util import DirForDate, OR, MultiOR


def Predict(df, funcs):
  X, prediction = Transform([df.last_era_update - df.last_era_update_time], df.actual_runway_arrival - df.last_era_update)
  prediction.fill(0)
  for f in funcs:
    prediction += f.predict(X)
  prediction /= len(funcs)
  assert len(prediction) == len(df.last_era_update), (len(prediction), len(df.last_era_update))
  print 'Should be 0', CountNan(prediction)
  default_ra = df.scheduled_runway_arrival + df.actual_runway_departure - df.scheduled_runway_departure
  default_ga = df.scheduled_gate_arrival + df.actual_runway_departure - df.scheduled_runway_departure
  df['actual_runway_arrival'] = MultiOR(df.last_era_update + prediction, df.last_era_update, df.last_ega_update, default_ra, df.scheduled_gate_arrival, default_ga)
  #print 'PPP', CountNan(df.actual_runway_arrival)
  df['actual_gate_arrival'] = MultiOR(df.last_ega_update, default_ga, df.scheduled_gate_arrival)
  return df


def RoundPredictions(df):
  R = lambda x: int(x + .5)
  df['actual_runway_arrival'] = pd.Series(df.actual_runway_arrival.map(R, na_action='ignore'), dtype=int)
  df['actual_gate_arrival'] = pd.Series(df.actual_gate_arrival.map(R, na_action='ignore'), dtype=int)

def main():
  output = os.path.join(local_constants.OUTPUT_DIR, 'models1_output.csv')
  with open(os.path.join(local_constants.OUTPUT_DIR, 'models1')) as fin:
    funcs = pickle.load(fin)
  need_header = True
  with open(output, 'w') as fout:
    for n in range(26, 31):
      par_dir = os.path.join(DirForDate('2012-11-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR))
      fpath = os.path.join(par_dir, 'good', 'flighthistory.csv')
      df = pd.read_csv(fpath, index_col='flight_history_id')
      df_pred = Predict(df, funcs)
      test_flights_path = os.path.join(par_dir, 'test_flights.csv')
      df_test_flights = pd.read_csv(test_flights_path, index_col='flight_history_id')
      public_predictions = df_test_flights.join(df_pred, lsuffix='left')
      #RoundPredictions(public_predictions)
      public_predictions.to_csv(fout, cols=['actual_runway_arrival', 'actual_gate_arrival'],
                                           header=need_header)
      print CountNan(public_predictions.actual_runway_arrival)
      print CountNan(public_predictions.actual_gate_arrival)
      need_header = False

    for n in range(1, 10):
      par_dir = os.path.join(DirForDate('2012-12-%02d' % n, parent_dir=local_constants.LEADERBOARD_DATA_DIR))
      fpath = os.path.join(par_dir, 'good', 'flighthistory.csv')
      df = pd.read_csv(fpath, index_col='flight_history_id')
      df_pred = Predict(df, funcs)
      test_flights_path = os.path.join(par_dir, 'test_flights.csv')
      df_test_flights = pd.read_csv(test_flights_path, index_col='flight_history_id')
      public_predictions = df_test_flights.join(df_pred, lsuffix='left')
      #RoundPredictions(public_predictions)
      public_predictions.to_csv(fout, cols=['actual_runway_arrival', 'actual_gate_arrival'],
                                header=need_header)
      print CountNan(public_predictions.actual_runway_arrival)
      print CountNan(public_predictions.actual_gate_arrival)
      need_header = False


if __name__ == "__main__":
  main()
