import gflags
import sys
from main.io import convert
from main.io.feature import *

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def main():
  # TODO: Parse only 3 columns.
  convert.ParseTestData(FLAGS.raw_data_file)
  score = ParseFeature('score')
  other_score = ParseFeature('other_score')
  average_score = FloatFeature(((a + b)/2. for a, b in zip(score, other_score)), 'Average score')
  average_score.SaveToFile('average_score')
  OutputAsScore(average_score, 'ole_score')


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)
