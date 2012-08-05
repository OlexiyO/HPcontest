from main.algo import grad_boost
from main.algo.grad_boost import KappaForPredictor, AveragePredictor
from main.base import util
from main.experiments import processing, ml_params
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


def PredictForSignals(q, list_of_signals, mods_for_training=4, boost_params={}):
  if boost_params is None:
    boost_params = {}
  preds = [grad_boost.Approximate(list_of_signals, q, extra_filter=util.FMod(k), boost_params=boost_params)
           for k in range(mods_for_training)]
  av_p = AveragePredictor(preds, [util.FMod(k) for k in range(mods_for_training)])
  return KappaForPredictor(av_p, list_of_signals, [q], extra_filter=util.FMod(4))
  v1 = [KappaForPredictor(av_p, list_of_signals, [q], extra_filter=util.FMod(k)) for k in range(5)]
  value = KappaForPredictor(av_p, list_of_signals, [q])
  print q, '%.2f' % value, util.PrintList(v1)
  return value


def main():
  # Todo:
  # 1. Automatically pick best model for every question.
  # 4. Try new signals.
  # 2. Try kappa as loss function.
  # 3. Try better loss function.
  N_EST = 150
  boost_params = dict(min_samples_leaf=5, min_samples_split=5, max_depth=1, n_estimators=N_EST, learn_rate=.3)
  list_of_signals = [G.num_words, G.is_crap, G.word_length, G.answer_length, G.num_sentences, G.choice]
  ml_params.PlotNumberOfEstimators(9, list_of_signals, mods_for_training=range(4), boost_params=boost_params, steps=N_EST)
  return
  vs = []
  for q in range(10):
    if q == 9:
      list_of_signals.append(G.choice)
    dd = []
    for msl in [3, 4, 5]:
      for n_estimators in range(30, 50, 5):
        for max_depth in range(1, 6):
          varz = dict(min_samples_leaf=msl, min_samples_split=msl, n_estimators=n_estimators, max_depth=max_depth)
          v = PredictForSignals(q, list_of_signals, boost_params=varz)
          dd.append((-v, varz))

  # vs.append()
  #print kappa.mean_quadratic_weighted_kappa(vs)

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