import gflags
from main.base.util import FTrue
from main.io import signal
from main.io.signal import G, MAX_SCORES

from main.metrics import kappa

FLAGS = gflags.FLAGS

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def Transform(score, max_score):
  if score <= 0:
    return 0
  elif score >= 100:
    return max_score
  else:
    return int(max_score + 1) * int(score) / 100


def FilterAndScaleScores(raw_scores, extra_filter, q):
  filtered = [s for i, s in enumerate(raw_scores)
              if G.question[i] == q and extra_filter(i)]
  if not filtered:
    print 'No scores filtered!', q
  M = signal.MaxScore(MAX_SCORES[q])
  # We think that scores are between 0 and 100.
  return [Transform(value, M) for value in filtered]


def EvalPerQuestion(raw_scores, extra_filter=FTrue, only_questions=None):
  golden = G.average_score if FLAGS.use_average_score else G.score
  if only_questions is None:
    only_questions = range(10)
  else:
    assert only_questions
    assert all(0 <= q < signal.NUM_QUESTIONS for q in only_questions), only_questions
  assert len(golden) == len(raw_scores), '%d != %d' % (len(golden), len(raw_scores))
  vals = [signal.UNKNOWN] * signal.NUM_QUESTIONS
  for q in only_questions:
    scaled_scores = FilterAndScaleScores(raw_scores, extra_filter, q)
    filtered_golden_scores = [v for i, v in enumerate(golden)
                              if G.question[i] == q and extra_filter(i)]
    assert len(scaled_scores) == len(filtered_golden_scores)
    vals[q] = kappa.quadratic_weighted_kappa(scaled_scores, filtered_golden_scores)
  return vals


def Eval(raw_scores, extra_filter=FTrue, only_questions=None):
  vals = EvalPerQuestion(raw_scores, extra_filter=extra_filter, only_questions=only_questions)
  known_vals = filter(lambda v: v != signal.UNKNOWN, vals)
  return float(sum(known_vals)) / len(known_vals)

