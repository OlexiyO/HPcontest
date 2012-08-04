from main.metrics.kappa import histogram, confusion_matrix, quadratic_weighted_kappa
from sklearn import ensemble

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class KappaCase(unittest.TestCase):

  def testHistogram(self):
    self.assertEqual([0, 0, 0, 0], histogram([]))
    self.assertEqual([1, 1, 1, 1], histogram([0, 1, 2, 3]))
    self.assertEqual([3, 0, 1, 2], histogram([0, 2, 3, 0, 3, 0]))
    self.assertEqual([0, 3, 0, 0], histogram([1, 1, 1]))

  def testConfusionMatrix(self):
    C1 = [[1, 0, 0],
          [0, 1, 0],
          [0, 0, 1]]
    self.assertEqual(C1, confusion_matrix([0, 1, 2], [0, 1, 2], max_rating=2))
    C2 = [[0, 0, 1],
          [0, 1, 0],
          [1, 0, 0]]
    self.assertEqual(C2, confusion_matrix([2, 1, 0], [0, 1, 2], max_rating=2))
    self.assertEqual(C2, confusion_matrix([0, 1, 2], [2, 1, 0], max_rating=2))
    C3 = [[0, 0, 1],
          [0, 0, 0],
          [0, 0, 0]]
    self.assertEqual(C3, confusion_matrix([0], [2], max_rating=2))

  def testQWK(self):
    self.assertEqual(1, quadratic_weighted_kappa([0, 1, 2, 3], [0, 1, 2, 3]))
    self.assertEqual(-1, quadratic_weighted_kappa([3, 0, 3, 0], [0, 3, 0, 3]))
    self.assertEqual(0, quadratic_weighted_kappa([2, 2, 2, 2], [1, 1, 1, 1]))
    self.assertEqual(0, quadratic_weighted_kappa([3, 3, 3, 3], [0, 0, 0, 0]))
    self.assertAlmostEqual(-0.15384615, quadratic_weighted_kappa([2, 2, 2, 2, 0, 2], [2, 2, 2, 2, 2, 1]))
    self.assertAlmostEqual(-0.2, quadratic_weighted_kappa([2, 2, 2, 2, 1, 2], [2, 2, 2, 2, 2, 1]))
    self.assertAlmostEqual(0.76923076, quadratic_weighted_kappa([2, 2, 2, 2, 2, 0], [2, 2, 2, 2, 2, 1]))
    self.assertAlmostEqual(0.875, quadratic_weighted_kappa([0, 0, 1, 1, 2, 2, 3, 3], [0, 0, 1, 1, 2, 2, 2, 2]))
    self.assertAlmostEqual(0.916666666, quadratic_weighted_kappa([0, 0, 1, 1, 2, 2, 3, 3], [0, 0, 1, 1, 3, 3, 3, 3]))

    # self.assertEqual(0, quadratic_weighted_kappa([3, 3, 3, 3], [3, 3, 3, 3])) # DivByZero


if __name__ == '__main__':
  unittest.main()
