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
  tmp = line.strip().split()
  while len(tmp) < cnt:
    tmp += ' '
  return tmp[:cnt - 1] + [' '.join(tmp[cnt - 1:])]


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

  def ValuesForQuestion(self, q):
    return [value for id, value in enumerate(self) if G.question[id] == q]

  def ItemsForQuestion(self, q):
    return [(id, value) for id, value in enumerate(self) if G.question[id] == q]


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


def Binary(fA, fB, Func, comment='', T=FloatFeature):
  return T(map(Func, zip(fA, fB)), comment)


def Unary(fA, Func, comment, T=FloatFeature):
  return T(map(Func, fA), comment)


G = FeatureStorage()


UNKNOWN = -111
NUM_QUESTIONS = 10
MAX_SCORES = [3, 3, 2, 2, 3, 3, 2, 2, 2, 2]
assert len(MAX_SCORES) == NUM_QUESTIONS

def MaxScore(question):
  assert 0 <= question < NUM_QUESTIONS
  return MAX_SCORES[question]


