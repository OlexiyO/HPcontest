import re
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


def GenerateBasicFeatures():
  assert os.path.isdir(FLAGS.data_dir)
  assert Exists('ids')
  assert Exists('score')
  assert Exists('other_score')
  assert Exists('question')
  assert Exists('answer')
  G.Define('average_score', Binary(G.score, G.other_score, lambda (a, b): (a + b / 2.)))
  G.Define('consistent_score', Binary(G.score, G.other_score, lambda (a, b): 1 if abs(a - b) <= 1 else 0, T=IntFeature))
  G.Define('good_score', Binary(G.average_score, G.consistent_score, lambda (a, b): a if b else -10))
  G.Define('answer_length', Unary(G.answer, len, comment='answer_length', T=IntFeature))
  G.Define('num_words', Unary(G.answer, NumWords, comment='NumWords', T=IntFeature))
  G.Define('num_sentences', Unary(G.answer, NumSentences, comment='num_sentences', T=IntFeature))
  G.Define('word_length', Binary(G.num_words, G.answer_length, lambda (a,b): float(b) / a))
