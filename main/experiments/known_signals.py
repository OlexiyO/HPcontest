import re
from main.experiments import processing
from main.io import signal
from main.io.signal import Binary, Unary, IntFeature, G

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import gflags
import os

FLAGS = gflags.FLAGS


def Exists(feature_name):
  filepath = os.path.join(FLAGS.data_dir, feature_name)
  return os.path.exists(filepath)


def NumWords(text):
  return len(re.sub('\W+', ' ', text).split())


def NumSentences(text):
  s = text.strip() + '. '
  return (len(re.findall('\? ', s)) + len(re.findall('\! ', s)) + len(re.findall('\. *[A-Z]', s)) +
          len(re.findall('\. *\Z', s)))


def GenerateTrainingFeatures():
  # Those features do not exist in real data.
  assert Exists('score')
  assert Exists('other_score')
  G.Define('average_score', Binary(G.score, G.other_score, lambda (a, b): (a + b / 2.)))
  G.Define('consistent_score', Binary(G.score, G.other_score, lambda (a, b): 1 if abs(a - b) <= 1 else 0, T=IntFeature))
  G.Define('good_score', Binary(G.average_score, G.consistent_score, lambda (a, b): a if b else -10))


def GenerateCrap():
  craps = [ 0 ] * len(G.ids)
  for id, q in enumerate(G.question):
    if q == 9 and G.choice[id] == -1:
      craps[id] = 1
      print G.ids[id]
    elif len(filter(str.isupper, G.answer[id])) * 2 > len(G.answer[id]):
      craps[id] = 1
      print G.ids[id]

  return signal.IntFeature(craps, 'Is really bad answer')


def GenerateBasicFeatures():
  assert os.path.isdir(FLAGS.data_dir)
  assert Exists('ids')
  assert Exists('question')
  assert Exists('raw_answer')
  processing.FixLastQuestion()
  G.Define('answer_length', Unary(G.answer, len, comment='answer_length', T=IntFeature))
  G.Define('num_words', Unary(G.answer, NumWords, comment='NumWords', T=IntFeature))
  G.Define('num_sentences', Unary(G.answer, NumSentences, comment='num_sentences', T=IntFeature))
  G.Define('word_length', Binary(G.num_words, G.answer_length, lambda (a,b): float(b) / a if a else 0))
  if not G._KnownFeature('is_crap'):
    G.Define('is_crap', GenerateCrap())
