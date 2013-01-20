# Classes representing models.

import cPickle as pickle
import numpy as np
from sklearn.ensemble import gradient_boosting
from flight_quest.util import assertSameLen, BestScoreFrom


def LoadPredictor(fname):
  with open(fname) as fin:
    res = pickle.load(fin)
  assert isinstance(res, BasePredictor)
  return res


class BasePredictor(object):

  def predict(self, *args, **kwargs):
    # Do not rename -- so it will match scipy methods.
    raise NotImplementedError()

  def Save(self, fname):
    with open(fname, 'w') as fout:
      pickle.dump(self, fout)


class AveragePredictor(BasePredictor):

  def __init__(self, *args):
    if len(args) == 1 and isinstance(args[0], list):
      self._predictors = args[0]
    else:
      self._predictors = args

    assert len(self._predictors) > 1
    assert all(hasattr(a, 'predict') for a in self._predictors)

  def predict(self, *args, **kwargs):
    return sum(p.predict(*args, **kwargs) for p in self._predictors) / len(self._predictors)


class PostProcessedPredictor(BasePredictor):
  # For cases when we take a model or other predictor, and modify it afterwards

  def __init__(self, other, func):
    """Takes another model and somehow modifies its output.

    Args:
      other: BasePredictor
      func: Takes float, outputs float.
    """
    self.other = other
    self.func = func

  def predict(self, *args, **kwargs):
    initial_output = self.other.predict(*args, **kwargs)
    return np.array(map(self.func, initial_output))


class OOBPredictor(BasePredictor):

  def __init__(self, predictors, bag_filters):
    """.

    Args:
      bag_filters: List of np.arrays. bag_filters[B][E] = True if element E belongs to bag B.

    """
    assertSameLen(bag_filters, predictors)
    self._predictors = predictors
    self._bag_filters = bag_filters

    assert len(self._predictors) > 1
    assert all(hasattr(a, 'predict') for a in self._predictors)

  def CutAtBestStep(self, X, y, num_steps):
    predicted = [y * 0 for _ in range(num_steps)]
    count = y * 0
    for bag_filter, predictor in zip(self._bag_filters, self._predictors):
      not_in_bag = True ^ bag_filter
      count += not_in_bag
      assert hasattr(predictor, 'staged_decision_function'), predictor
      for i, y_pred in enumerate(predictor.staged_decision_function(X)):
        if i > num_steps:
          break
        w = not_in_bag * y_pred.flatten()
        predicted[i] += w
    assert all(cnt == count[0] for cnt in count), count
    LOSS_F = gradient_boosting.LOSS_FUNCTIONS['ls'](1)
    step_losses = [LOSS_F(y, pred / count) for pred in predicted]

    best_step = BestScoreFrom(step_losses)
    print 'Cutting at step %d' % best_step
    for clf in self._predictors:
      clf.estimators_ = clf.estimators_[:(best_step + 1)]

  def predict(self, *args, **kwargs):
    return sum(p.predict(*args, **kwargs) for p in self._predictors) / len(self._predictors)