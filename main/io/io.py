import os

import gflags
from main.io.signal import G, FloatFeature, IntFeature, StringFeature
from main.metrics.metrics import ToScore

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def SaveAsScores(ids, vals, filename):
  assert os.path.isdir(FLAGS.data_dir), FLAGS.data_dir
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as f:
    f.write('id,essay_score\n')
    f.writelines('%d,%d\n' % t for t in zip(ids, vals))


def OutputAsScore(signal, filename):
  ids = G.ids
  assert len(ids) == len(signal)
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as fout:
    fout.writelines('%d,%d\n' % t for t in zip(ids, ToScore(signal)))


