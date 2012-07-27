import re
from main.io.feature import Binary, ParseFeature, Unary, IntFeature

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


def GenerateKnownFeatures():
  assert os.path.isdir(FLAGS.data_dir)
  assert Exists('ids')
  assert Exists('score')
  assert Exists('other_score')
  assert Exists('question')
  assert Exists('answer')
  for name in ['ids', 'score', 'other_score', 'question', 'answer']:
    globals()[name] = ParseFeature(name)

  if not Exists('average_score'):
     F = lambda (a, b): (a + b) / 2.
     av_score = Binary(score, other_score, F, comment='average_score')
     av_score.SaveToFile('average_score')

  if not Exists('answer_length'):
    answer_length = Unary(answer, len, comment='answer_length', T=IntFeature)
    answer_length .SaveToFile('answer_length')

  if not Exists('num_words'):
    num_words = Unary(answer, NumWords, comment='num_words', T=IntFeature)
    num_words.SaveToFile('num_words')

  if not Exists('num_sentences'):
    num_sentences = Unary(answer, NumSentences, comment='num_sentences', T=IntFeature)
    num_sentences.SaveToFile('num_sentences')


