from main.io.feature import *

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import os
import sys

import gflags
FLAGS = gflags.FLAGS

def main():
  score = ParseFeature('score')
  other_score = ParseFeature('other_score')
  average_score = ParseFeature('average_score')
  print 'scores', Eval(score)
  print 'second scores', Eval(other_score)
  print 'aver', Eval(average_score)


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)