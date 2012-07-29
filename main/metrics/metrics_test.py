from main.metrics.metrics import ToScore

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest

class MetricsTestCase(unittest.TestCase):

  def testToScore(self):
    V = [0., .5, 3.5, 4.9, 2.99, 1.51, 1.99, 2.495, -2, -2.5, -.1]
    self.assertEquals([0, 1, 3, 3, 3, 2, 2, 2, 0, 0, 0], ToScore(V))



if __name__ == '__main__':
  unittest.main()

