from numpy.ma.core import ids
from main.experiments.known_features import GenerateKnownFeatures

from main.io.feature import *

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import os
import sys

import gflags
FLAGS = gflags.FLAGS

ALL_FEATURES = ['ids', 'score', 'other_score', 'question', 'answer',
                'average_score']


def DefineFeatures():
  for name in ALL_FEATURES:
    globals()[name] = ParseFeature(name)


def main():
  GenerateKnownFeatures()
  DefineFeatures()
  '''
  print 'scores', Eval(score), EvalOnValidation(score)
  print 'second scores', Eval(other_score), EvalOnValidation(other_score)
  print 'aver', Eval(average_score), EvalOnValidation(average_score)
  vals = IntFeature([id % 4 for id in ids], '')
  print 'vals', Eval(vals), EvalOnValidation(vals)
  '''



if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)