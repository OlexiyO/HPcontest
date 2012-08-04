from main.base import util
from main.io.signal import G
from main.metrics import kappa

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

from sklearn.ensemble import GradientBoostingRegressor

class AveragePredictor(object):

  def __init__(self, predictors):
    self._predictors = predictors

  def predict(self, data):
    return sum(p.predict(data) for p in self._predictors) / len(self._predictors)


def Approximate(signals, q, extra_filter=util.FTrue):
  #samples = [[k, 5*k, 2*k] for k in range(100)]
  is_consistent = lambda id: extra_filter(id) and G.consistent_score[id]
  all_samples = [signal.ValuesForQuestion(q, extra_filter=is_consistent) for signal in signals]
  samples = zip(*all_samples)
  labels = G.score.ValuesForQuestion(q, extra_filter=is_consistent)
  return GradientBoostingRegressor(min_samples_leaf=5, min_samples_split=5, n_estimators=50).fit(samples, labels)


def DoPrediction(signals, q, extra_filter=util.FTrue):
  predictor = Approximate(signals, q, extra_filter=extra_filter)
  #print ScoreForPredictor(predictor, signals, q, extra_filter=extra_filter)
  return predictor


def ScoreForPredictor(predictor, signals, q, extra_filter=util.FTrue):
  S = lambda id: [signal[id] for signal in signals]
  predicted = [int(round(predictor.predict(S(id)))) for id, _ in G.question.ItemsForQuestion(q, extra_filter=extra_filter)]
  actual = G.score.ValuesForQuestion(q, extra_filter=extra_filter)
  return kappa.quadratic_weighted_kappa(actual, predicted)
