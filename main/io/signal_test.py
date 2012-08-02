from main.io import signal
from main.io.signal import StringFeature, G

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class SignalTestCase(unittest.TestCase):
  def testBasic(self):
    letters = signal.StringFeature(['a', 'b', 'c', 'd'], 'trololo')
    self.assertEqual(4, len(letters))
    self.assertEqual('b', letters[1])
    doubled = signal.Unary(letters, lambda s: s + s, 'doubled', T=signal.StringFeature)
    self.assertEqual(4, len(doubled))
    self.assertEqual('cc', doubled[2])

  def testIters(self):
    letters = signal.StringFeature(['a', 'b', 'c', 'd'], 'trololo')
    Q = signal.IntFeature([0, 0, 1, 2], 'question')
    G.Define('question', Q, override=True, save=False)
    self.assertEqual(['a', 'b'], letters.ValuesForQuestion(0))
    self.assertEqual(['d'], letters.ValuesForQuestion(2))
    self.assertEqual([2], Q.ValuesForQuestion(2))


if __name__ == '__main__':
  unittest.main()
