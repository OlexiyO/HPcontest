from main.io.signal import G

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

cutoff = [35, 45, 50, 35, 45, 50, 60, 40, 40, 35]
values = [50, 50, 100, 50, 50, 50, 100, 100, 100, 100]


def Version0(ind, *_argv):
  q = G.question[ind]
  if G.num_words[ind] < cutoff[q]:
    return 0
  else:
    return values[q]


def Version1(ind, *_argv):
  q = G.question[ind]
  if G.num_words[ind] < cutoff[q] or G.is_crap[ind] == 1:
    return 0
  else:
    return values[q]
