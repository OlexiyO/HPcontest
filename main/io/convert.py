__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

from main.io import io, feature

import gflags
import os

gflags.DEFINE_string('raw_data_file', 'c:\\Dev\\Kaggle\\asap_sas\\raw\\train.tsv', 'Input file.')
gflags.DEFINE_string('output_dir', None, 'Output directory.')

gflags.MarkFlagAsRequired('output_dir')
FLAGS = gflags.FLAGS

def ParseTestData(filepath, output_dir):
  question = feature.IntFeature()
  score1 = feature.IntFeature()
  score2 = feature.IntFeature()
  answer = feature.StringFeature()
  with open(filepath) as fin:
    past_first = False
    for line in fin:
      # First line is crap
      if not past_first:
        past_first = True
        continue
      cols = io.SplitIntoN(line, 5)
      id = int(cols[0])
      question.AddValue(id, cols[1])
      score1.AddValue(id, cols[2])
      score2.AddValue(id, cols[3])
      answer.AddValue(id, cols[4])




def main(_):
  ParseTestData(FLAGS.raw_data_file, FLAGS.output_dir)