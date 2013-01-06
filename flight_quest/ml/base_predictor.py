# Classes representing models.

import cPickle as pickle
import numpy as np


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
