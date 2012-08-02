from main.io.signal import G

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def Model(ind, vars):
  if G.num_words[ind] < vars['min_word_cutoff']:
    return 0
  return G.answer_length[ind] * vars['ans_len'] + G.num_sentences[ind] * vars['num_sent']


def VerySimple2(ind, vars):
  if G.num_words[ind] < vars['min_word_cutoff']:
    return 0
  else:
    return 50


def VerySimple3(ind, vars):
  if G.num_words[ind] < vars['min_word_cutoff']:
    return 0
  else:
    return 100


def VerySimple0(ind, vars):
  if G.num_words[ind] < vars['min_word_cutoff']:
    return 0
  else:
    return 0


def VerySimple1(ind, vars):
    if G.num_words[ind] < vars['min_word_cutoff']:
      return 0
    else:
      return 30



      # all zeroes         ['0.617', '0.530', '0.680', '0.791', '0.948', '0.943', '0.719', '0.520', '0.568', '0.543']
    # len < 20 ? 0 : 100 ['0.865', '0.896', '0.625', '0.573', '0.818', '0.830', '0.501', '0.662', '0.768', '0.790']

