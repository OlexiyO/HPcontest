from main.io.feature import Filter, ToScore

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class FeatureTestCase(unittest.TestCase):
  def testFilter(self):
    V = [0., 0.1, 0.2, 0.3, 0.4, 0.5]
    self.assertEqual([0.1], Filter(V, [1], 5))
    self.assertEqual([0.1, 0.4], Filter(V, [1], 3))
    self.assertEqual([0.1, 0.4], Filter(V, [1, 4], 5))
    self.assertEqual([0., 0.5], Filter(V, [0], 5))
    self.assertRaises(AssertionError, Filter, V, [-1], 5)
    self.assertRaises(AssertionError, Filter, V, [0, 5], 5)

  def testToScore(self):
    V = [0., .5, 3.5, 1.51, 1.99, 2.495]
    self.assertEquals([0, 1, 4, 2, 2, 2], ToScore(V))



if __name__ == '__main__':
  unittest.main()

