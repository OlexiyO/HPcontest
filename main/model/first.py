import gflags
import sys
from main.io import convert, io
from main.io.olefeature import *

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

gflags.DEFINE_string('model_scores_file', 'model_scores', 'File to save output.')


def main():
  convert.ParseLeaderboardData(FLAGS.raw_data_file)
  ids = ParseFeature('ids')
  vals = IntFeature([id % 4 for id in ids], '')
  io.SaveAsScores(ids, vals, FLAGS.model_scores_file)


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)
