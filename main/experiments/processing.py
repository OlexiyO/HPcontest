import re
from main.base import util
from main.io import signal
from main.io.signal import G

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import os

CORPUS_DIR = 'c:\\Dev\\Kaggle\\asap-sas\\help_data'


def FilterOneAnswer(corpus, line):
  words = line.split()
  W = len(words)
  for n in range(W - 1):
    w1 = words[n].lower()
    w2 = words[n + 1].lower()
    if w1 == 'dog' and w2 == 'house':
      #print words[n], words[n + 1]
      words[n] = words[n] + words[n + 1]
      words[n + 1] = ''
      continue

    while w2 and not w2[-1].isalnum():
      w2 = w2[:-1]
    if w1 not in corpus or w2 not in corpus:
      continue
    common = w1 + w2
    if (common in corpus) and corpus[common] >= min(corpus[w1], corpus[w2]) - 1:
      print words[n], words[n + 1]
      words[n] = words[n] + words[n + 1]
      words[n + 1] = ''
      continue
  return ' '.join(w for w in words if w)


def BuildCorpus(q, text_lines):
  res = {}
  for n, text in enumerate(text_lines):
    words = map(lambda x: x.lower(), re.findall('\w+', text))
    for w_ in words:
      w = w_.lower()
      res[w] = res.get(w, 0) + 1

  with open(os.path.join(CORPUS_DIR, 'dict_%d' % q), 'w') as f:
    f.write('%s' % util.PrintDict(res))
  return res


class CorpusStorage(object):

  def __init__(self):
    self._corpora = []

  def GetCorpus(self, item):
    if item not in self._corpora:
      with open(os.path.join(CORPUS_DIR, 'dict_%d' % item)) as f:
        self._corpora[item] = eval(f.read())
    return self._corpora[item]

C = CorpusStorage()


def ProcessRawAnswer():
  if G._KnownFeature('choice') and G._KnownFeature('answer'):
    return
  R = len(G.raw_answer)
  answer = [0] * R
  corpora = [0] * 10
  choice = [0] * R
  for n in range(9):
    corpora[n] = BuildCorpus(n, G.raw_answer.ValuesForQuestion(n))

  for id, line in enumerate(G.raw_answer):
    if G.question[id] != 9:
      answer[id] = G.raw_answer[id]
      choice[id] = -1

  options = ['lightgray', 'darkgray', 'white', 'black']
  new_data = []
  for id, line in G.raw_answer.ItemsForQuestion(9):
    if G.question[id] == 9:
      ii = line.find('::')
      ss = util.OnlyLetters(line[:ii].lower())
      choice[id] = options.index(ss) if ss in options else -1
      new_data.append(line[ii + 2:])

  G.Define('choice', signal.IntFeature(choice, 'Choice question.'))

  while True:
    corpora[9] = BuildCorpus(9, new_data)
    dd = []
    for n, line in enumerate(new_data):
      s = FilterOneAnswer(corpora[9], new_data[n])
      if s != new_data[n]:
        dd.append((new_data[n], s))
        #print new_data[n]
        #print s
        #print ' '
        new_data[n] = s
    if not dd:
      break
    print '-----------------------'


  ids_9 = G.question.ItemsForQuestion(9)
  assert len(ids_9) == len(new_data)
  for id, val in zip(ids_9, new_data):
    answer[id[0]] = val
  G.Define('answer', signal.StringFeature(answer, 'Original: answer'))