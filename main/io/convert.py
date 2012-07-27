__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

from main.io import io, feature

import gflags
import sys

gflags.DEFINE_string('raw_data_file', None, 'Input file.')

FLAGS = gflags.FLAGS

gflags.MarkFlagAsRequired('raw_data_file')


def ParseTestData(filepath):
  ids, question, score, other_score, answer = [], [], [], [], []
  with open(filepath) as fin:
    past_first = False
    for line in fin:
      # First line is crap
      if not past_first:
        past_first = True
        continue
      cols = io.SplitIntoN(line, 5)
      ids.append(cols[0])
      question.append(cols[1])
      score.append(cols[2])
      other_score.append(cols[3])
      answer.append(cols[4])

  feature.IntFeature(map(int, ids), 'Original: id').SaveToFile('ids')
  feature.IntFeature(map(int, question), 'Original: question').SaveToFile('question')
  feature.IntFeature(map(int, score), 'Original: score').SaveToFile('score')
  feature.IntFeature(map(int, other_score), 'Original: other_score').SaveToFile('other_score')
  feature.StringFeature(answer, 'Original: answer').SaveToFile('answer')


def ParseLeaderboardData(filepath):
  ids, question, answer = [], [], []
  with open(filepath) as fin:
    past_first = False
    for line in fin:
      # First line is crap
      if not past_first:
        past_first = True
        continue
      cols = io.SplitIntoN(line, 3)
      ids.append(cols[0])
      question.append(cols[1])
      answer.append(cols[2])

  feature.IntFeature(map(int, ids), 'Original: id').SaveToFile('ids')
  feature.IntFeature(map(int, question), 'Original: question').SaveToFile('question')
  feature.StringFeature(answer, 'Original: answer').SaveToFile('answer')


def main():
  ParseTestData(FLAGS.raw_data_file)


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)