from main.base import util

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import gflags
import os

FLAGS = gflags.FLAGS
gflags.DEFINE_string('data_dir', 'c:\\Dev\\Kaggle\\asap-sas\\features', 'Input/output directory.')
gflags.DEFINE_bool('use_average_score', False, 'Whether use average score as ideal.')
# All docs with ids % validation_denom == validation_nom considered to be CV set.
gflags.DEFINE_integer('validation_nom', 0, '.')
gflags.DEFINE_integer('validation_denom', 5, '.')


def SplitIntoN(line, cnt):
  # Parses line by splitting into exactly N parts.
  tmp = line.strip().split()
  while len(tmp) < cnt:
    tmp += ' '
  return tmp[:cnt - 1] + [' '.join(tmp[cnt - 1:])]


def ParseFeature(filename):
  # Parses file with feature data.
  filepath = os.path.join(FLAGS.data_dir, filename)
  assert os.path.exists(filepath), filepath
  CLASSES = {'STRING': StringFeature, 'INT': IntFeature, 'FLOAT': FloatFeature, 'COMPLEX': ComplexFeature}
  with open(filepath) as fin:
    line_raw = fin.readline()
    assert line_raw[0] == '#', line_raw
    T = line_raw.strip()[2:]
    CLAZZ = CLASSES[T]
    vals = (CLAZZ.ParseValue(SplitIntoN(line, 2)[1]) for line in fin if line[0] != '#')
    res = CLAZZ(vals, 'Parsed from %s' % filepath)

  res.name = filename
  return res


def ParseFromDir(dirpath):
  return [(name, ParseFeature(name)) for name in os.listdir(dirpath)]


# TODO: easy way to get all values for question Q.

class FeatureStorage(object):
  def __init__(self):
    self.__dict__['_features'] = {}

  def _FileExists(self, name):
    return os.path.exists(os.path.join(FLAGS.data_dir, name))

  def _KnownFeature(self, name):
    return (name in self._features) or self._FileExists(name)

  def Define(self, name, what, override=False, save=True):
    if override or not self._KnownFeature(name):
      if save:
        what.SaveToFile(name)
      self._features[name] = what
      what.name = name

  def __getattr__(self, name):
    if name in self._features:
      return self._features[name]
    # Do not use self._features.setdefault(name, ParseFeature(name)) -- because ParseFeature will be called.
    assert self._FileExists(name)
    print 'Parsing', name
    feat = ParseFeature(name)
    self._features[name] = feat
    return feat

  def __setattr__(self, name, value):
    raise NotImplementedError()

  def __getitem__(self, name):
    raise NotImplementedError()

  def __setitem__(self, name):
    raise NotImplementedError()


class _Feature(list):
  def __init__(self, values, comment=''):
    super(_Feature, self).__init__(values)
    self._comment = comment

  def GetType(self):
    raise NotImplementedError

  @classmethod
  def ParseValue(cls, _value):
    raise NotImplementedError

  def SaveToFile(self, filename, separator='\t', with_comment=True):
    filepath = os.path.join(FLAGS.data_dir, filename)
    assert not os.path.exists(filepath), filepath
    with open(filepath, 'w') as fout:
      if with_comment:
        fout.write('# %s\n' % self.GetType())
        fout.write('# %s\n' % self._comment)
      fout.writelines('%d%s%s\n' % (t[0], separator, t[1]) for t in enumerate(self))

  def ValuesForQuestion(self, q, extra_filter=util.FTrue):
    return [value for id, value in enumerate(self) if (G.question[id] == q) and extra_filter(id)]

  def ItemsForQuestion(self, q, extra_filter=util.FTrue):
    return [(id, value) for id, value in enumerate(self) if (G.question[id] == q) and extra_filter(id)]


class IntFeature(_Feature):
  def GetType(self):
    return 'INT'

  @classmethod
  def ParseValue(cls, value):
    return int(value)


class StringFeature(_Feature):
  def GetType(self):
    return 'STRING'

  @classmethod
  def ParseValue(cls, value):
    return value


class FloatFeature(_Feature):
  def GetType(self):
      return 'FLOAT'

  @classmethod
  def ParseValue(cls, value):
    return float(value)


class ComplexFeature(_Feature):
  def GetType(self):
    return 'COMPLEX'

  @classmethod
  def ParseValue(cls, value):
    return eval(value)



def Binary(fA, fB, Func, comment='', T=FloatFeature):
  return T(map(Func, zip(fA, fB)), comment)


def Unary(fA, Func, comment, T=FloatFeature):
  return T(map(Func, fA), comment)

# Storage for answer-level features.
G = FeatureStorage()
# Storage for question-level features.
Q = FeatureStorage()

UNKNOWN = -111
NUM_QUESTIONS = 10


def IdsForQuestion(q, extra_filter=util.FTrue):
  return (id for id, _ in G.question.ItemsForQuestion(q, extra_filter=extra_filter))


def ListOfSignals(list_of_signals, q, extra_filter=util.FTrue):
  F = lambda id: [S[id] for S in list_of_signals]
  return [F(id) for id in IdsForQuestion(q, extra_filter=extra_filter)]