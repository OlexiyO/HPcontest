import numpy as np

def PrepareForTraining(iX, iy):
  # Transforms (list of Series, Series) --> numpy structures.
  Xs, y = FilterOnlyWithY(iX, iy)
  return np.array(Xs).transpose(), y


def Transform(iX, iy):
  # Transforms (list of Series, Series) --> numpy structures.
  Xs = [np.array(x) for x in iX]
  return np.array(Xs).transpose(), np.array(iy)


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


def SplitIndices(L, test_ratio):
  test_indices = set([])
  while len(test_indices) < L * test_ratio:
    test_indices.add(np.random.randint(0, L - 1))

  all_indices = set(xrange(L))
  set_to_np_array = lambda s: np.array([x for x in s])
  return set_to_np_array(all_indices - test_indices), set_to_np_array(test_indices)