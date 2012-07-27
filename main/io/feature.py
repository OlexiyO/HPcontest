from main.io.io import SplitIntoN
from main.math import metrics

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import gflags
import os

FLAGS = gflags.FLAGS
gflags.DEFINE_string('data_dir', 'c:\\Dev\\Kaggle\\asap-sas\\output', 'Input/output directory.')
gflags.DEFINE_bool('use_average_score', False, 'Whether use average score as ideal.')
# All docs with ids % validation_denom == validation_nom considered to be CV set.
gflags.DEFINE_integer('validation_nom', 0, '.')
gflags.DEFINE_integer('validation_denom', 5, '.')


class Feature(list):
  def __init__(self, values, comment):
    super(Feature, self).__init__(values)
    self._comment = comment

  def GetType(self):
    raise NotImplementedError

  def PrintValue(self, value):
    raise NotImplementedError

  def SaveToFile(self, filename, separator='\t', with_comment=True):
    filepath = os.path.join(FLAGS.data_dir, filename)
    assert not os.path.exists(filepath), filepath
    with open(filepath, 'w') as fout:
      if with_comment:
        fout.write('# %s\n' % self.GetType())
        fout.write('# %s\n' % self._comment)
      fout.writelines('%d%s%s\n' % (t[0], separator, self.PrintValue(t[1])) for t in enumerate(self))


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


def Filter(what, noms, denom):
  assert all((0 <= N < denom) for N in noms)
  return [w for n, w in enumerate(what) if n % denom in noms]


def Eval(scores):
  golden = ParseFeature('average_score') if FLAGS.use_average_score else ParseFeature('score')
  assert len(golden) == len(scores), '%d != %d' % (len(golden), len(scores))
  good_noms = [k for k in range(FLAGS.validation_denom) if k != FLAGS.validation_nom]
  return metrics.quadratic_weighted_kappa(
    Filter(ToScore(scores), good_noms, FLAGS.validation_denom),
    Filter(golden, good_noms, FLAGS.validation_denom))


def EvalOnValidation(scores):
  golden = ParseFeature('average_score') if FLAGS.use_average_score else ParseFeature('score')
  assert len(golden) == len(scores), '%d != %d' % (len(golden), len(scores))
  return metrics.quadratic_weighted_kappa(
    Filter(ToScore(scores), [FLAGS.validation_nom], FLAGS.validation_denom),
    Filter(golden, [FLAGS.validation_nom], FLAGS.validation_denom))


def OutputAsScore(what, filename):
  ids = ParseFeature('ids')
  assert len(ids) == len(what)
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as fout:
    fout.writelines('%d,%d\n' % t for t in zip(ids, ToScore(what)))


def Binary(fA, fB, Func, comment, T=FloatFeature):
  return T(map(Func, zip(fA, fB)), comment)


def Unary(fA, Func, comment, T=FloatFeature):
  return T(map(Func, fA), comment)