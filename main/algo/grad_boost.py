from main.base import util
from main.io.signal import G
from main.metrics import kappa

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

from sklearn.ensemble import GradientBoostingRegressor


class AveragePredictor(object):

  def __init__(self, predictors, filters):
    # Returns average value of several predictions.
    # predictors: list of objects with predict(data) method.
    # filters: list of functions. filters[i][id] == True if answer number id was used when building predictor[i].
    assert len(predictors) == len(filters)
    self._predictors = predictors
    self._filters = filters
    self.L = len(predictors)

  def predict(self, data):
    return sum(p.predict(data) for p in self._predictors) / self.L

  def predict_out_of_bag(self, id, data):
    scores = [p.predict(data) for p, f in zip(self._predictors, self._filters) if not f(id)]
    return sum(scores) / len(scores)

  def Loss(self, a, b):
    return sum(p.loss_(a, b) for p in self._predictors) / self.L

  def PredictionAtSteps(self, signals_data):
    import numpy
    # Input: N ids, K signals each
    # S steps * N elements * 1 score for each
    N = len(signals_data)
    results = [[v.copy() for v in p.staged_decision_function(signals_data)]
               for p in self._predictors]
    S = len(results[0])
    T1 = [0] * N
    R = results[0]
    for R1 in results[1:]:
      R = numpy.add(R, R1)
    ans = [T1[:] for _ in range(S)]
    for k in range(S):
      for m in range(N):
        ans[k][m] = R[k][m][0] / self.L
        #ans[k][m] = sum(results[i][k][m] for i in range(self.L)) / self.L
    return ans


def Approximate(signals, q, extra_filter=util.FTrue, boost_params=None):
  if boost_params is None:
    boost_params = {}
  is_consistent = lambda id: extra_filter(id) and G.consistent_score[id]
  all_samples = [signal.ValuesForQuestion(q, extra_filter=is_consistent) for signal in signals]
  samples = zip(*all_samples)
  labels = G.score.ValuesForQuestion(q, extra_filter=is_consistent)
  return GradientBoostingRegressor(**boost_params).fit(samples, labels)


def KappaForPredictor(predictor, signals, questions, extra_filter=util.FTrue, out_of_bag=True):
  S = lambda id: [signal[id] for signal in signals]
  F = predictor.predict_out_of_bag if out_of_bag else predictor.predict
  predicted = [int(round(F(id, S(id))))
               for id, q in enumerate(G.question) if q in questions and extra_filter(id)]
  actual = [G.score[id] for id, q in enumerate(G.question) if q in questions and extra_filter(id)]
  return kappa.quadratic_weighted_kappa(actual, predicted)
