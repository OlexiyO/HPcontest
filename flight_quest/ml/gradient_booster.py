from sklearn import ensemble
from sklearn import metrics
from flight_quest.ml import base_predictor
from flight_quest.ml.base_predictor import AveragePredictor
from flight_quest.ml.cv_util import PredictRunwayRMSE
from flight_quest.ml.data_util import PrepareForTraining, _SplitIntoTrainAndTest


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


def _CutAtBestStep(clf, X_test, y_test):
  test_scores = ComputeStepScores(clf, X_test, y_test)
  T = 0
  best_step = test_scores[T:].index(min(test_scores[T:])) + T
  #print 'Best step:', best_step
  clf.estimators_ = clf.estimators_[:(best_step + 1)]
  return best_step


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
  #print '%d docs have y defined out of total %d docs' % (L, len(iy))

  X_test, X_train, y_test, y_train = _SplitIntoTrainAndTest(X, y, test_ratio)

  params = {'n_estimators': 500, 'max_depth': 1, 'min_samples_split': 5,
            'learn_rate': 0.1, 'loss': 'ls'}
  if param_overrides:
    params.update(param_overrides)
  clf = ensemble.GradientBoostingRegressor(**params)
  clf.fit(X_train, y_train)

  best_func = _CutAtBestStep(clf, X_test, y_test)
  _PrintDebugInfo(best_func, X_test, X_train, y_test, y_train)
  return clf


def LearnGradientBoostInTwoHalves(iX, iy, param_overrides=None, min_steps=10):
  """Learns a model to approximate iy from iX.

  Args:
    iX: List of pandas.Series.
    iy: pandas.Series.
    param_overrides: Dict of param overrides for GradientBoost algorithm.
    test_ratio: Which part to put into test set.
    min_steps: int. If training for any part of the data took more than this number of steps, we retrain.

  Returns:
    Model.
  """
  assert all(len(x) == len(iy) for x in iX), '%s != %d' % (map(len, iX), len(iy))

  X, y = PrepareForTraining(iX, iy)

  L = len(y)
  #print '%d docs have y defined out of total %d docs' % (L, len(iy))

  while True:
    X_1, X_2, y_1, y_2 = _SplitIntoTrainAndTest(X, y, .5)

    params = {'n_estimators': 500, 'max_depth': 1, 'min_samples_split': 5,
              'learn_rate': 0.1, 'loss': 'ls'}
    if param_overrides:
      params.update(param_overrides)

    clf1 = ensemble.GradientBoostingRegressor(**params)
    clf1.fit(X_1, y_1)
    step1 = _CutAtBestStep(clf1, X_2, y_2)
    if step1 < min_steps:
      continue
    clf2 = ensemble.GradientBoostingRegressor(**params)
    clf2.fit(X_2, y_2)
    step2 = _CutAtBestStep(clf2, X_1, y_1)
    if step1 >= min_steps and step2 >= min_steps:
      return base_predictor.AveragePredictor(clf1, clf2)
    '''
    if step1 >= min_steps:
      if step2 >= min_steps:
        return base_predictor.AveragePredictor(clf1, clf2)
      else:
        return clf1
    else:
      return clf2
    '''


def Train(DF, input_func, output_func, training_filter=None, fname=None, DF_test=None,
          min_steps=10):
  """Perform gradient boost training on DFs.

  Args:
    DF: List of pd.DataFrame, used for training.
    input_func: Function, which takes a pd.DataFrame and returns a list of pd.Series,
        which will be used as input to ML training.
    outut_func: Function, which takes a pd.DataFrame and returns one pd.Series,
        which will be used as target to approximate during ML training.
    training_filter: Function, which takes a pd.DataFrame and returns one pd.Series.
        Output will be used as filter on which elements to use for training.
    fname: (string) If not empty, will save the resulting predictor to file with this name.
    DF_test: List of pd.DataFrame, used for outputting metrics only.
    min_steps: Passed to LearnGradientBoostInTwoHalves, see its docstring for details.

  Returns:
    BasePredictor.
  """
  funcs = []
  for df in DF:
    series_in = input_func(df)
    series_out = output_func(df)
    if training_filter:
      computed_filter = training_filter(df)
      series_in = [s[computed_filter] for s in series_in]
      series_out = series_out[training_filter(df)]
    funcs.append(LearnGradientBoostInTwoHalves(
        series_in, series_out, param_overrides={'n_estimators': 1250}, min_steps=min_steps))
  predictor = AveragePredictor(funcs)
  if fname:
    predictor.Save(fname)
  train_score = PredictRunwayRMSE(DF, predictor, input_func, 'A')
  if DF_test:
    test_score = PredictRunwayRMSE(DF_test, predictor, input_func, 'B')
    return predictor, test_score
  else:
    return predictor, train_score