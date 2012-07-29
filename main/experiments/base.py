from numpy.ma.core import ids
from main.experiments.known_features import GenerateBasicFeatures

from main.io.olefeature import *

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import os
import re
import sys

import gflags
FLAGS = gflags.FLAGS

ALL_FEATURES = ['ids', 'score', 'other_score', 'question', 'answer',
                'average_score']


def PrintInOrder(D):
  vals = sorted(D.iteritems(), key=lambda x: -x[1])
  return '{\n%s}\n' % ',\n'.join('"%s": %d' % v for v in vals)


def CountWords(q):
  D = {}
  for n, text in enumerate(answer):
    if question[n] != q:
      continue
    words = map(lambda x: x.lower(), re.findall('\w+', text))
    for w in words:
      D[w] = D.get(w, 0) + 1

  DIR = 'c:\\Dev\\Kaggle\\asap-sas\\help_data'
  with open(os.path.join(DIR, 'dict_%d' % q), 'w') as f:
    f.write('%s' % PrintInOrder(D))


def main():
  GenerateBasicFeatures()



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