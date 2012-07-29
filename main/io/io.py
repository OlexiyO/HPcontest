import os

import gflags
FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def SplitIntoN(line, cnt):
  tmp = line.strip().split()
  assert len(tmp) >= cnt, 'Expected at least %d parts in line: "%s"' % (cnt, line)
  return tmp[:cnt - 1] + [' '.join(tmp[cnt - 1:])]


def SaveAsScores(ids, vals, filename):
  assert os.path.isdir(FLAGS.data_dir), FLAGS.data_dir
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as f:
    f.write('id,essay_score\n')
    f.writelines('%d,%d\n' % t for t in zip(ids, vals))
