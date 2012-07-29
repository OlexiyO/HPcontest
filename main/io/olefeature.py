from main.io.io import SplitIntoN
from main.metrics import kappa

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import gflags
import os

FLAGS = gflags.FLAGS
gflags.DEFINE_string('data_dir', 'c:\\Dev\\Kaggle\\asap-sas\\features', 'Input/output directory.')
gflags.DEFINE_bool('use_average_score', False, 'Whether use average score as ideal.')
# All docs with ids % validation_denom == validation_nom considered to be CV set.
gflags.DEFINE_integer('validation_nom', 0, '.')
gflags.DEFINE_integer('validation_denom', 5, '.')


class FeatureStorage(object):
  def __init__(self):
    self.__dict__['_features'] = dict(ParseFromDir(FLAGS.data_dir))

  def Define(self, name, what):
    if name not in self._features:
      what.SaveToFile(name)
      self._features[name] = what

  def __getattr__(self, name):
    return self._features[name]

  def __setattr__(self, name, value):
    raise NotImplementedError()

  def __getitem__(self, name):
    raise NotImplementedError()

  def __setitem__(self, name):
    raise NotImplementedError()


class _Feature(list):
  def __init__(self, values, comment):
    super(_Feature, self).__init__(values)
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


class IntFeature(_Feature):
  def PrintValue(self, value):
    return '%d' % value

  def GetType(self):
    return 'INT'


class StringFeature(_Feature):
  def PrintValue(self, value):
    return value

  def GetType(self):
    return 'STRING'


class FloatFeature(_Feature):
  def PrintValue(self, value):
    return '%f' % value

  def GetType(self):
      return 'FLOAT'


def ParseFromDir(dirpath):
  return [(name, ParseFeature(name)) for name in os.listdir(dirpath)]


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


def OutputAsScore(what, filename):
  ids = ParseFeature('ids')
  assert len(ids) == len(what)
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert not os.path.exists(filepath), filepath
  with open(filepath, 'w') as fout:
    fout.writelines('%d,%d\n' % t for t in zip(ids, ToScore(what)))


def Binary(fA, fB, Func, comment='', T=FloatFeature):
  return T(map(Func, zip(fA, fB)), comment)


def Unary(fA, Func, comment, T=FloatFeature):
  return T(map(Func, fA), comment)


G = FeatureStorage()