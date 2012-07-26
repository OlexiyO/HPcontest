from main.io.io import SplitIntoN
from main.math import metrics

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import gflags
import os

FLAGS = gflags.FLAGS
gflags.DEFINE_string('data_dir', 'c:\\Dev\\Kaggle\\asap-sas\\output', 'Input/output directory.')
gflags.DEFINE_bool('use_average_score', False, 'Whether use average score as ideal.')


class Feature(list):
  def __init__(self, values, comment):
    super(Feature, self).__init__(values)
    self._comment = comment

  def GetType(self):
    raise NotImplementedError

  def PrintValue(self, value):
    raise NotImplementedError

  def SaveToFile(self, filename):
    filepath = os.path.join(FLAGS.data_dir, filename)
    assert not os.path.exists(filepath), filepath
    with open(filepath, 'w') as fout:
      fout.write('# %s\n' % self.GetType())
      fout.write('# %s\n' % self._comment)
      fout.writelines('%d\t%s\n' % (t[0], self.PrintValue(t[1])) for t in enumerate(self))


class IntFeature(Feature):
  def PrintValue(self, value):
    return '%d' % value

  def GetType(self):
    return 'INT'


class StringFeature(Feature):
  def PrintValue(self, value):
    return value

  def GetType(self):
    return 'STRING'


class FloatFeature(Feature):
  def PrintValue(self, value):
    return '%f' % value

  def GetType(self):
      return 'FLOAT'


def ParseFeature(filename):
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert os.path.exists(filepath), filepath
  FS = {'STRING': str, 'INT': int, 'FLOAT': float}
  CLASSES = {'STRING': StringFeature, 'INT': IntFeature, 'FLOAT': FloatFeature}
  with open(filepath) as fin:
    line_raw = fin.readline()
    assert line_raw[0] == '#', line_raw
    T = line_raw.strip()[2:]
    F = FS[T]
    vals = (F(SplitIntoN(line, 2)[1]) for line in fin if line[0] != '#')
    res = CLASSES[T](vals, 'Parsed from %s' % filepath)

  return res


def ToScore(scores):
  return map(int, map(round, scores))


def Eval(scores):
  golden = ParseFeature('average_score') if FLAGS.use_average_score else ParseFeature('score')
  assert len(golden) == len(scores), '%d != %d' % (len(golden), len(scores))
  return metrics.quadratic_weighted_kappa(ToScore(scores), golden)


def OutputAsScore(what, filename):
  ids = ParseFeature('ids')
  assert len(ids) == len(what)
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as fout:
    fout.writelines('%d,%d\n' % t for t in zip(ids, ToScore(what)))