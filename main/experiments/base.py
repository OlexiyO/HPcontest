from main.algo import grad_boost
from main.algo.grad_boost import ScoreForPredictor, AveragePredictor
from main.base import util
from main.experiments import processing
from main.experiments.known_signals import GenerateBasicFeatures, GenerateTrainingFeatures
from main.experiments.misc import *

from main.metrics import metrics, kappa
from main.model import models

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import sys

import gflags
FLAGS = gflags.FLAGS


def RawScoresForModel(model, vars, extra_filter=util.FTrue):
  # Build raw scores for a model.
  # Raw scores is a full vector, each value 0 to 100.
  return [model(ind, vars) if extra_filter(ind) else -111 for ind in range(len(G.ids))]


def TryFixing():
  # Compare two algorithms for fixing typos.
  v = processing.BuildCorpus(9, G.answer.ValuesForQuestion(9))
  tt = G.answer.ValuesForQuestion(9)
  for a, b in v.iteritems():
    if len(a) == 1:
      pass
      #print a, b
  res1 = processing.RemoveSpacesFromAnswer(v, tt)
  res2 = processing.RemoveSpacesFromAnswer(v, tt) # Replace by another algo

  diff = res2 - res1

  for (w1, w2) in diff:
    common = w1 + w2
    print w1, w2, common, v[w1], v[w2], v[common]
  return


def CheckModel(model, selector):
  # Run model on selected ids. Print metrics per question.
  scores = RawScoresForModel(model, {}, extra_filter=selector)
  v2 = metrics.EvalPerQuestion(scores, extra_filter=selector)
  print '%.2f' % (sum(v2) / len(v2)), util.PrintList(v2)


def PredictForSignals(sig):
  preds = [grad_boost.DoPrediction(sig, 9, extra_filter=util.FMod(m)) for m in range(4)]
  av_p = AveragePredictor(preds)
  #print preds[0]
  v1 = [ScoreForPredictor(av_p, sig, 9, extra_filter=util.FMod(k)) for k in range(5)]
  print util.PrintList(v1)


def main():
  '''
  sig1 = [G.num_words, G.is_crap]
  PredictForSignals(sig1)
  sig2 = [G.num_words, G.is_crap, G.choice]
  PredictForSignals(sig2)
  sig3 = [G.num_words, G.is_crap, G.choice, G.num_sentences]
  PredictForSignals(sig3)
  '''
  sig4 = [G.num_words, G.is_crap, G.choice, G.word_length, G.answer_length]
  PredictForSignals(sig4)

  return
# TODO: show difference between models!
  GenerateBasicFeatures()
  GenerateTrainingFeatures()

  return
  # TODO: try to integrate some other signal into "all zeroes" model
  # TODO: Find most popular words for each question, try to use
  # TODO: use different target function

  '''
  for id, elem in enumerate(G.num_words):
      if elem < 3:
        print id, G.question[id], G.score[id], G.other_score[id], G.answer[id]
  '''

  vars = {'min_word_cutoff': 3.,
          'ans_len': .5,
          'num_sent': 10., }
  # TODO: compute scores for pub leaderboard.
  #scores = ScoresForModel(VerySimple2, vars)

  print 'Current'
  for k in range(5):
    CheckModel(models.Version0, util.FMod(k))

  for k in range(5):
    CheckModel(models.Version1, util.FMod(k))

  return
  data0 = []
  data1 = []
  data2 = []
  data3 = []
  ks = range(5, 100, 5)
  for k in ks:
    vars['min_word_cutoff'] = k
    scores0 = RawScoresForModel(VerySimple0, vars, extra_filter=util.FMod(1))
    data0.append(metrics.EvalPerQuestion(scores0, extra_filter=util.FMod(1)))
    scores1 = RawScoresForModel(VerySimple1, vars, extra_filter=util.FMod(1))
    data1.append(metrics.EvalPerQuestion(scores1, extra_filter=util.FMod(1)))
    scores2 = RawScoresForModel(VerySimple2, vars, extra_filter=util.FMod(1))
    data2.append(metrics.EvalPerQuestion(scores2, extra_filter=util.FMod(1)))
    scores3 = RawScoresForModel(VerySimple3, vars, extra_filter=util.FMod(1))
    data3.append(metrics.EvalPerQuestion(scores3, extra_filter=util.FMod(1)))
    # print k, '%.2f' % (sum(v2) / len(v2)), ['%.3f' % v for v in v2]

  cutoff = []
  value = []
  score = []
  for q in range(10):
    s0 = [(-data0[i][q], (k, 0)) for i, k in enumerate(ks)]
    s1 = [(-data1[i][q], (k, 30)) for i, k in enumerate(ks)]
    s2 = [(-data2[i][q], (k, 50)) for i, k in enumerate(ks)]
    s3 = [(-data3[i][q], (k, 100)) for i, k in enumerate(ks)]
    x = sorted(s0 + s1 + s2 + s3)
    score.append(-x[0][0])
    cutoff.append(x[0][1][0])
    value.append(x[0][1][1])

  print cutoff
  print value
  print kappa.mean_quadratic_weighted_kappa(score), util.PrintList(score)

# TODO: cross validation.

  #v1 = metrics.EvalPerQuestion(scores, extra_filter=FMod51)
  #print ['%.3f' % v for v in v1]
  #v2 = metrics.EvalPerQuestion(scores, extra_filter=FValidation)
  #print ['%.3f' % v for v in v2]


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)