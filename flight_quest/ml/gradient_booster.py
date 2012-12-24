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


def Transpose(Xs):
  return np.array(Xs).transpose()


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


def PrepareForBoost(iX, iy):
  # Transforms (list of Series, Series) --> numpy structures.
  Xs, y = FilterOnlyWithY(iX, iy)
  X = Transpose(Xs)
  return X, y


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

  X, y = PrepareForBoost(iX, iy)

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


def main():
  funcs = [0] * 30
  DF = [0] * 30
  for n in range(13, 20):
    DF[n] = util.LoadForDay('2012-11-%d' % n, parent_dir=local_constants.PARENT_DATA_DIR)
    funcs[n] = LearnGradientBoost([DF[n].runway_delay], DF[n].taxi_arrival_delta,
                                  param_overrides={'n_estimators': 250})  # Change 1250 --> 250 --> 150 --> 5

  T = 20 - 13
  data = [([0] * T) for _ in range(T + 2)]
  for n in range(13, 20):
    X, y = PrepareForBoost([DF[n].runway_delay], DF[n].taxi_arrival_delta)
    P = y * 0
    OOB = y * 0
    for m in range(13, 20):
      p1 = funcs[m].predict(X)
      data[m - 13][n - 13] = metrics.mean_squared_error(p1, y)
      P += p1
      if m != n:
        OOB += p1
    data[20 - 13][n - 13] = metrics.mean_squared_error(P / T, y)
    data[21 - 13][n - 13] = metrics.mean_squared_error(OOB / (T - 1), y)

  for i, d in enumerate(data):
    ind = i + 13
    print i + 13 if i < T else 'AV', ['%.1f' % x for x in d]


if __name__ == "__main__":
  main()
