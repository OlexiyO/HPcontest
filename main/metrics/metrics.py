import gflags
from main.io.olefeature import ParseFeature, G
from main.metrics import kappa

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def FTrue(*args, **kwargs):
  return True


def Eval(scores, filter=FTrue, questions=None):
  golden = G.average_score if FLAGS.use_average_score else G.score
  if questions is None:
    questions = range(1, 10)
  else:
    assert questions
  assert len(golden) == len(scores), '%d != %d' % (len(golden), len(scores))
  vals = []
  for q in questions:
    F = lambda id: filter(id) and G.question[id] == q
    vals.append(kappa.quadratic_weighted_kappa(filter(F, scores), filter(F, golden)))

  return sum(vals) / len(vals)


def ToScore(scores):
  def Func(x):
    val = int(round(x))
    return min(3, max(val, 0))
  return map(Func, scores)
