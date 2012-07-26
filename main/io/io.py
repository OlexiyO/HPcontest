__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def SplitIntoN(line, cnt):
  tmp = line.strip().split()
  assert len(tmp) >= cnt, 'Expected at least %d parts in line: "%s"' % (cnt, line)
  return tmp[:cnt - 1] + [' '.join(tmp[cnt - 1:])]
