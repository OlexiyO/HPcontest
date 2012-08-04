from main.io.signal import SplitIntoN, G, Q

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

from main.io import io, signal

import gflags
import sys

gflags.DEFINE_string('raw_data_file', None, 'Input file.')

FLAGS = gflags.FLAGS

gflags.MarkFlagAsRequired('raw_data_file')


def ParseTrainingData(filepath):
  # Parses training data -- in (id, question, score1, score2, answer) format.
  ids, question, score, other_score, raw_answer = [], [], [], [], []
  with open(filepath) as fin:
    past_first = False
    for line in fin:
      # First line is crap
      if not past_first:
        past_first = True
        continue
      cols = SplitIntoN(line, 5)
      ids.append(cols[0])
      q = int(cols[1]) - 1
      question.append(q)
      score.append(cols[2])
      other_score.append(cols[3])
      raw_answer.append(cols[4])
      assert 0 <= int(cols[2]) <= Q.MaxScore[q], line
      assert 0 <= int(cols[3]) <= Q.MaxScore[q], line

  signal.IntFeature(map(int, ids), 'Original: id').SaveToFile('ids')
  signal.IntFeature(map(int, question), 'Original: question').SaveToFile('question')
  signal.IntFeature(map(int, score), 'Original: score').SaveToFile('score')
  signal.IntFeature(map(int, other_score), 'Original: other_score').SaveToFile('other_score')
  signal.StringFeature(raw_answer, 'Original: raw_answer').SaveToFile('raw_answer')


def ParseLeaderboardData(filepath):
  # Parses test data -- in (id, question, answer) format.
  ids, question, raw_answer = [], [], []
  with open(filepath) as fin:
    past_first = False
    for line in fin:
      # First line in file is non-data.
      if not past_first:
        past_first = True
        continue
      cols = SplitIntoN(line, 3)
      ids.append(cols[0])
      question.append(int(cols[1]) - 1)
      raw_answer.append(cols[2])

  signal.IntFeature(map(int, ids), 'Original: id').SaveToFile('ids')
  signal.IntFeature(map(int, question), 'Original: question').SaveToFile('question')
  signal.StringFeature(raw_answer, 'Original: raw_answer').SaveToFile('raw_answer')



def main():
  # Run this once to generate basic signals.
  ParseTrainingData(FLAGS.raw_data_file)


if __name__ == '__main__':
  try:
    _ = FLAGS(sys.argv)  # parse flags
    main()
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)