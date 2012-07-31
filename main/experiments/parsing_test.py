from main.experiments.known_signals import NumWords, NumSentences

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class ParseTestCase(unittest.TestCase):
  def testNumWords(self):
    self.assertEqual(1, NumWords('abcd'))
    self.assertEqual(0, NumWords(''))
    self.assertEqual(3, NumWords('abcd,E.F'))
    self.assertEqual(2, NumWords('Hello!World'))
    self.assertEqual(2, NumWords(' Hello ! \tWorld '))
    self.assertEqual(3, NumWords('How are you?'))

  def testNumSentences(self):
    self.assertEqual(1, NumSentences('abcd'))
    self.assertEqual(1, NumSentences('Abcd.'))
    self.assertEqual(1, NumSentences('Hello world!'))
    self.assertEqual(2, NumSentences('Hello! I am John'))
    self.assertEqual(2, NumSentences('Hello! I am John, and I am ten. '))
    self.assertEqual(2, NumSentences('Hello! I am John, and I am ten...'))
    self.assertEqual(3, NumSentences('Hello! I am John, and I am ten. Well  '))
    self.assertEqual(2, NumSentences('Hello,How are you.I am John, and I am ten.'))


if __name__ == '__main__':
  unittest.main()
