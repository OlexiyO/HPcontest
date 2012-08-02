from main.io import convert

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class ConvertTestCase(unittest.TestCase):
  def testFilter(self):
    corpus = {'dog': 123, 'house': 342, "wamt": 1, "exposure": 1, "eflects": 1,
              'r': 4, 'temp': 5, 'erature': 1, 'temperature': 10, 'ed': 5, 'red': 5}
    S = 'Dog HouSE temp erature. temperature was r ed.'
    self.assertEqual('DogHouSE temperature. temperature was red.',
                     convert.FilterOneAnswer(corpus, S))


if __name__ == '__main__':
  unittest.main()
