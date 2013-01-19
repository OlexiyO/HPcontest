import numpy as np
from sklearn import ensemble
from sklearn import metrics
from flight_quest.ml import base_predictor
from flight_quest.ml.base_predictor import AveragePredictor, OOBPredictor
from flight_quest.ml.cv_util import PredictRunwayRMSE
from flight_quest.ml.data_util import PrepareForTraining, _SplitIntoTrainAndTest
from flight_quest.util import BestScoreFrom


def _PrintDebugInfo(func, X_test, X_train, y_test, y_train):
  mse = metrics.mean_squared_error(y_train, func.predict(X_train))
  print("TrainOnSeriesOfDF MSE: %.4f" % mse)
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
  best_step = BestScoreFrom(test_scores, from_step=T)
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
              'min_samples_leaf': 5,
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
      print step1, step2
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

def LearnGradientBoostInBags(iX, iy, num_bags, bag_mods, param_overrides=None):
  """Learns a model to approximate iy from iX.

  Args:
    iX: List of pandas.Series.
    iy: pandas.Series.
    num_bags: How many bags to create
    bag_mods: For doc i, it falls into bag k if ((i + k) % num_bags) < bag_mods
    param_overrides: Dict of param overrides for GradientBoost algorithm.

  Returns:
    Model.
  """
  assert 0 < bag_mods < num_bags, (bag_mods, num_bags)
  assert all(len(x) == len(iy) for x in iX), '%s != %d' % (map(len, iX), len(iy))
  X, y = PrepareForTraining(iX, iy)
  L = len(y)

  bag_filters = []
  for bag in range(num_bags):
    in_bag_f = lambda ind: ((ind + bag) % num_bags) < bag_mods
    # np.array() for filters is essential.
    bag_filters.append(np.array([in_bag_f(ind) for ind in range(L)]))

  params = {'n_estimators': 1500, 'max_depth': 1, 'min_samples_split': 5, 'min_samples_leaf': 5,
            'learn_rate': 0.1, 'loss': 'ls'}
  if param_overrides:
    params.update(param_overrides)

  funcs = []
  for bag in range(num_bags):
    print 'Learning bag', bag
    clf1 = ensemble.GradientBoostingRegressor(**params)
    clf1.fit(X[bag_filters[bag]], y[bag_filters[bag]])
    funcs.append(clf1)

  predictor = OOBPredictor(funcs, bag_filters)
  predictor.CutAtBestStep(X, y, params['n_estimators'])
  return predictor


def LearnStochasticGradientBoost(iX, iy, iX_test, iy_test, param_overrides=None, min_steps=10):
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
  X_test, y_test = PrepareForTraining(iX_test, iy_test)

  L = len(y)
  #print '%d docs have y defined out of total %d docs' % (L, len(iy))

  while True:
    params = {'n_estimators': 1500, 'max_depth': 1, 'min_samples_split': 5, 'min_samples_leaf': 5,
              'learn_rate': 0.1, 'loss': 'ls'}
    if param_overrides:
      params.update(param_overrides)

    clf1 = ensemble.GradientBoostingRegressor(**params)
    clf1.fit(X, y)
    step1 = _CutAtBestStep(clf1, X_test, y_test)
    print step1
    if step1 >= min_steps:
      return clf1


def MergeDFs(DFs):
  assert DFs, 'List of DFs is empty'
  res = DFs[0]
  for df in DFs[1:]:
    res.append(df)
  return res


def TrainOnSeriesOfDF(DF, input_func, output_func, param_overrides, training_filter=None, fname=None, DF_test=None,
                      min_steps=10):
  """Perform gradient boost training on DFs.

  Args:
    DF: List of pd.DataFrame, used for training.
    input_func: Function, which takes a pd.DataFrame and returns a list of pd.Series,
        which will be used as input to ML training.
    outut_func: Function, which takes a pd.DataFrame and returns one pd.Series,
        which will be used as target to approximate during ML training.
    param_overrides: Dictionary to pass to gradient boost trainer.
    training_filter: Function, which takes a pd.DataFrame and returns one pd.Series.
        Output will be used as filter on which elements to use for training.
    fname: (string) If not empty, will save the resulting predictor to file with this name.
    DF_test: List of pd.DataFrame, used for outputting metrics only.
    min_steps: Passed to LearnGradientBoostInTwoHalves, see its docstring for details.

  Returns:
    BasePredictor.
  """
  funcs = []
  param_overrides.setdefault('n_estimators', 1250)
  DF_united = MergeDFs(DF_test[0:3])

  test_in = input_func(DF_united)
  test_out = output_func(DF_united)

  for df in DF:
    series_in = input_func(df)
    series_out = output_func(df)

    if training_filter:
      computed_filter = training_filter(df)
      series_in = [s[computed_filter] for s in series_in]
      series_out = series_out[training_filter(df)]
    #funcs.append(LearnGradientBoostInTwoHalves(
    funcs.append(LearnStochasticGradientBoost(
        series_in, series_out, test_in, test_out, param_overrides=param_overrides, min_steps=min_steps))
  predictor = AveragePredictor(funcs)
  if fname:
    predictor.Save(fname)
  train_score = PredictRunwayRMSE(DF, predictor, input_func, name='A')
  if DF_test:
    test_score = PredictRunwayRMSE(DF_test[S:], predictor, input_func, name='B')
    return predictor, test_score
  else:
    return predictor, train_score


def TrainWithOOB(DF, DF_test, input_func, output_func, param_overrides, num_bags=5, bag_mods=3,
                 training_filter=None, fname=None):
  """Perform gradient boost training on DFs.

  Args:
    DF: One big pandas.DataFrame.
    DF_test: pd.DataFrame, used for print validation metrics after training. Not used during training.
    input_func: Function, which takes a pd.DataFrame and returns a list of pd.Series,
        which will be used as input to ML training.
    outut_func: Function, which takes a pd.DataFrame and returns one pd.Series,
        which will be used as target to approximate during ML training.
    param_overrides: Dictionary to pass to gradient boost trainer.
    training_filter: Function, which takes a pd.DataFrame and returns one pd.Series.
        Output will be used as filter on which elements to use for training.
    fname: (string) If not empty, will save the resulting predictor to file with this name.

  Returns:
    BasePredictor.
  """
  param_overrides.setdefault('n_estimators', 1000)

  training_in = input_func(DF)
  training_out = output_func(DF)

  if training_filter:
    computed_filter = training_filter(DF)
    training_in = [s[computed_filter] for s in training_in]
    training_out = training_out[computed_filter]
  predictor = LearnGradientBoostInBags(training_in, training_out, num_bags=num_bags, bag_mods=bag_mods,
                                       param_overrides=param_overrides)
  if fname:
    predictor.Save(fname)
  train_score = PredictRunwayRMSE([DF], predictor, input_func, name='A')
  test_score = PredictRunwayRMSE([DF_test], predictor, input_func, name='B')
  return predictor, test_score
