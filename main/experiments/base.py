from main.base import util
from main.experiments.known_signals import GenerateBasicFeatures
from main.experiments.misc import *

from main.io.signal import *
from main.metrics import metrics

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import os
import re
import sys

import gflags
FLAGS = gflags.FLAGS

ALL_FEATURES = ['ids', 'score', 'other_score', 'question', 'answer',
                'average_score']

def PrintInOrder(D):
  vals = sorted(D.iteritems(), key=lambda x: -x[1])
  return '{\n%s}\n' % ',\n'.join('"%s": %d' % v for v in vals)


def BuildCorpus(q):
  D = {}
  for n, text in enumerate(G.answer):
    if G.question[n] != q:
      continue
    words = map(lambda x: x.lower(), re.findall('\w+', text))
    for w in words:
      D[w] = D.get(w, 0) + 1

  DIR = 'c:\\Dev\\Kaggle\\asap-sas\\help_data'
  with open(os.path.join(DIR, 'dict_%d' % q), 'w') as f:
    f.write('%s' % PrintInOrder(D))


def ScoresForModel(model, vars, extra_filter=util.FTrue):
  return [model(ind, vars) if extra_filter(ind) else -111 for ind in range(len(G.ids))]


def main():
  GenerateBasicFeatures()
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
  FMod5 = lambda ind: (ind % 5) != 0
  FMod51 = lambda ind: (ind % 5) == 1
  FValidation = lambda ind: not FMod5(ind)
  # TODO: compute scores for pub leaderboard.
  scores = ScoresForModel(VerySimple2, vars)

  """
  data2 = []
  data3 = []
  # TODO: try return 0 always.
  ks = range(5, 100, 5)
  for k in range(5, 100, 5):
    vars['min_word_cutoff'] = k
    scores2 = ScoresForModel(VerySimple2, vars, extra_filter=FMod51)
    data2.append(metrics.EvalPerQuestion(scores2, extra_filter=FMod51))
    scores3 = ScoresForModel(VerySimple3, vars, extra_filter=FMod51)
    data3.append(metrics.EvalPerQuestion(scores3, extra_filter=FMod51))
    #print k, '%.2f' % (sum(v2) / len(v2)), ['%.3f' % v for v in v2]

  cutoff = []
  value = []
  score = []
  for q in range(10):
    s2 = [(-data2[i][q], (k, 50)) for i, k in enumerate(ks)]
    s3 = [(-data3[i][q], (k, 100)) for i, k in enumerate(ks)]
    x = sorted(s2 + s3)
    score.append(-x[0][0])
    cutoff.append(x[0][1][0])
    value.append(x[0][1][1])

  print cutoff
  print value
  print score
  """

  # TODO: cross validation.

  #v1 = metrics.EvalPerQuestion(scores, extra_filter=FMod51)
  #print ['%.3f' % v for v in v1]
  #v2 = metrics.EvalPerQuestion(scores, extra_filter=FValidation)
  #print ['%.3f' % v for v in v2]

  '''
  print 'scores', Eval(score), EvalOnValidation(score)
  print 'second scores', Eval(other_score), EvalOnValidation(other_score)
  print 'aver', Eval(average_score), EvalOnValidation(average_score)
  vals = IntFeature([id % 4 for id in ids], '')
  print 'vals', Eval(vals), EvalOnValidation(vals)
  '''


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)