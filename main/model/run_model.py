import gflags
import sys
from numpy.ma.core import ids
from main.experiments import misc, known_signals
from main.io import io, convert, signal
from main.io.signal import *
from main.metrics.metrics import Transform
from main.model import models

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

gflags.DEFINE_string('model_scores_file', 'model_scores', 'File to save output.')


def ToFinalScore(id, score):
  return Transform(score, signal.MaxScore(G.question[id]))


def SaveAsScores(vals, filename):
  assert os.path.isdir(FLAGS.data_dir), FLAGS.data_dir
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as f:
    f.write('id,essay_score\n')
    f.writelines('%d,%d\n' % t for t in zip(G.ids, vals))


def main():
  #convert.ParseLeaderboardData(FLAGS.raw_data_file)
  known_signals.GenerateBasicFeatures()
  print len(G.ids)
  print len(G.num_words)
  predictions = map(models.Version0, range(len(G.ids)))
  scores = [ToFinalScore(id, value) for id, value in enumerate(predictions)]
  io.SaveAsScores(scores, FLAGS.model_scores_file)


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)
