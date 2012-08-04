__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

def FTrue(*args, **kwargs):
  return True


def PrintList(lst):
  return ['%.3f' % v for v in lst]


def PrintDict(D):
  vals = sorted(D.iteritems(), key=lambda x: -x[1])
  return '{\n%s}\n' % ',\n'.join('"%s": %d' % v for v in vals)


def OnlyAlnum(s):
  return ''.join(q for q in s if q.isalnum())


