import os
import numpy as np
from sklearn import ensemble
from sklearn import metrics
from flight_quest import util
from flight_quest.io import local_constants


def SplitIndices(L, test_ratio):
  test_indices = set(np.random.random_integers(0, L - 1, int(L * test_ratio)))
  #test_indices = set(xrange(int(L * .2)))
  all_indices = set(xrange(L))
  set_to_np_array = lambda s: np.array([x for x in s])
  return set_to_np_array(all_indices - test_indices), set_to_np_array(test_indices)


def FilterOnlyWithY(iX, iy):
  F = lambda n: not np.isnan(iy[n])
  y = np.array(iy.select(F))
  Xs = [np.array(x.select(F)) for x in iX]
  return Xs, y


def _SplitIntoTrainAndTest(X, y, test_ratio):
  train_indices, test_indices = SplitIndices(len(y), test_ratio)
  y_train, y_test = y[train_indices], y[test_indices]
  X_train, X_test = X[train_indices], X[test_indices]
  return X_test, X_train, y_test, y_train


# Note: Model should be a class and not a function so we can pickle it.
class Model(object):

  def __init__(self, func, num_inputs):
    pass

  def Predict(self, X):
    assert isinstance(X, np.array)


def _PrintDebugInfo(func, X_test, X_train, y_test, y_train):
  mse = metrics.mean_squared_error(y_train, func.predict(X_train))
  print("Train MSE: %.4f" % mse)
  mse = metrics.mean_squared_error(y_test, func.predict(X_test))
  print("Test MSE: %.4f" % mse)


def ComputeStepScores(clf, X, y):
  test_scores = []
  for i, y_pred in enumerate(clf.staged_decision_function(X)):
    test_scores.append(clf.loss_(y, y_pred))
  return test_scores


def _PickBestFunction(clf, X_train, X_test, y_train, y_test):
  # TODO: Implement picking best step.
  test_scores = ComputeStepScores(clf, X_test, y_test)
  print 'Test:', test_scores
  train_scores = ComputeStepScores(clf, X_train, y_train)
  print 'Train:', train_scores
  #util.Plot(range(len(train_scores)), [train_scores, test_scores], style='-')
  return clf


def PrepareForTraining(iX, iy):
  # Transforms (list of Series, Series) --> numpy structures.
  Xs, y = FilterOnlyWithY(iX, iy)
  return np.array(Xs).transpose(), y


def Transform(iX, iy):
  # Transforms (list of Series, Series) --> numpy structures.
  y = np.array(iy)
  Xs = [np.array(x) for x in iX]
  return np.array(Xs).transpose(), y


def LearnGradientBoost(iX, iy, param_overrides=None, test_ratio=.2):
  """Learns a model to approximate iy from iX.

  Args:
    iX: List of pandas.Series.
    iy: pandas.Series.
    param_overrides: Dict of param overrides for GradientBoost algorithm.
    test_ratio: Which part to put into test set.

  Returns:
    Model.
  """
  assert all(len(x) == len(iy) for x in iX), '%s != %d' % (map(len, iX), len(iy))

  X, y = PrepareForTraining(iX, iy)

  L = len(y)
  print '%d docs have y defined out of total %d docs' % (L, len(iy))

  X_test, X_train, y_test, y_train = _SplitIntoTrainAndTest(X, y, test_ratio)

  params = {'n_estimators': 500, 'max_depth': 1, 'min_samples_split': 5,
            'learn_rate': 0.1, 'loss': 'ls'}
  if param_overrides:
    params.update(param_overrides)
  clf = ensemble.GradientBoostingRegressor(**params)
  clf.fit(X_train, y_train)

  best_func = _PickBestFunction(clf, X_train, X_test, y_train, y_test)
  _PrintDebugInfo(best_func, X_test, X_train, y_test, y_train)
  return clf


def PrintCVTable(DF, get_input_func, get_output_func, n_estimators):
  funcs = []
  for df in DF:
    funcs.append(LearnGradientBoost(
      get_input_func(df), get_output_func(df),
      param_overrides={'n_estimators': n_estimators}, test_ratio=.01))  # Change 1250 --> 250 --> 150 --> 5

  N = len(DF)
  data = [([0] * N) for _ in range(N + 2)]
  for n, df in enumerate(DF):
    X, y = PrepareForTraining(get_input_func(df), get_output_func(df))
    P = y * 0
    OOB = y * 0
    for m, f in enumerate(funcs):
      p1 = f.predict(X)
      data[m][n] = metrics.mean_squared_error(p1, y)
      P += p1
      if m != n:
        OOB += p1
    data[N][n] = metrics.mean_squared_error(P / N, y)
    data[N + 1][n] = metrics.mean_squared_error(OOB / (N - 1), y)

  for i, d in enumerate(data):
    print i + 13 if i < N else ('AV' if i == N else 'OOB'), ['%.1f' % x for x in d]


def BuildEstimation(df, funcs):
  df['ole_runway_arrival'] = util.OR(df.estimated_runway_arrival, df.scheduled_runway_arrival)
  gate_arrival = util.OR(df.estimated_gate_arrival, df.scheduled_gate_arrival)
  runway_delay = df.ole_runway_arrival - df.scheduled_runway_arrival

  X = Transpose([runway_delay])
  prediction = sum(func.predict(X) for func in funcs) / len(funcs)
  assert len(prediction) == len(df.flight_history_id)
  df['prediction'] = prediction #util.OR(prediction, gate_arrival * 0)
  df['before_adjust'] = gate_arrival
  df['x1'] = util.OR(df.estimated_gate_arrival, df.ole_runway_arrival + df.scheduled_taxi_arrival)
  df['x2'] = util.OR(df.estimated_gate_arrival, df.ole_runway_arrival + df.scheduled_taxi_arrival) + prediction
  df['x3'] = util.OR(df.x1 + util.AND(df.prediction, df.estimated_runway_arrival), df.x1)
  df['x4'] = util.OR(df.x1 + util.AND(df.prediction, df.estimated_runway_arrival), df.x1)


def main():
  #filter = OR(OR(df.actual_runway_arrival, df.actual_runway_departure), OR(df.actual_gate_arrival, df.actual_gate_departure))
  funcs = []
  for n in range(13, 22):
    df = util.LoadForDay('2012-11-%d' % n, parent_dir=local_constants.PARENT_DATA_DIR)
    funcs.append(LearnGradientBoost([df.runway_delay], df.taxi_arrival_delta,
                                    param_overrides={'n_estimators': 200}, test_ratio=.01))

  out_file = os.path.join(local_constants.LEADERBOARD_DATA_DIR, 'out1.csv')
  with open(out_file, 'w') as fout:
    for n in range(22, 26):
      df = util.LoadForDay('2012-11-%d' % n, parent_dir=local_constants.PARENT_DATA_DIR)
      BuildEstimation(df, funcs)
      cols_to_print = ['flight_history_id', 'ole_runway_arrival', 'ole_gate_arrival']
      #df.to_csv(fout, cols=cols_to_print, index=False, header=False)
      print 'runway: ', util.RMSE2(df.ole_runway_arrival, df.actual_runway_arrival)
      print 'gate before: ', util.RMSE2(df.before_adjust, df.actual_gate_arrival)
      print 'x1: ', util.RMSE2(df.x1, df.actual_gate_arrival)
      print 'x2: ', util.RMSE2(df.x2, df.actual_gate_arrival)
      print 'x3: ', util.RMSE2(df.x3, df.actual_gate_arrival)


if __name__ == "__main__":
  main()
