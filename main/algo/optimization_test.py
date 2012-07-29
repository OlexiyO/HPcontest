from main.algo.optimization import Gradient, GradientDescent

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest


class OptimizationTestCase(unittest.TestCase):
  def CheckDict(self, d1, d2, places=6):
    self.assertEquals(d1.keys(), d2.keys())
    for k in d1:
      self.assertAlmostEqual(d1[k], d2[k], places=places, msg='%s %.15f %.15f' % (k, d1[k], d2[k]))

  def testGradient(self):
    F1 = lambda vars: 2 * vars['x'] * vars['x'] + 3 * vars['y'] - 1
    point = {'x': 0, 'y': 0, 'z': 0}
    self.CheckDict({'y' : 1}, Gradient(F1, point, step=1e-9))
    point = {'x': 1, 'y': -1, 'z': 2}
    self.CheckDict({'x': .8, 'y' : .6}, Gradient(F1, point, step=1e-9))

    F2 = lambda vars: 2 * vars['x'] * vars['y'] + vars['y'] * vars['y']
    point = {'x': 0, 'y': 0, 'k': 0}
    self.CheckDict({}, Gradient(F2, point, step=1e-9))
    point = {'x': -3.5, 'y': 6}
    self.CheckDict({'x': 12/13., 'y': 5/13.}, Gradient(F2, point, step=1e-9))

  def testGradientDescent(self):
    F1 = lambda vars: 2 * vars['x'] * vars['x'] + 3 * pow(2 * vars['y'] - 4, 2.)
    point = {'x': 5, 'y': 5, 'z': 5}
    self.CheckDict({'x': 0, 'y': 2, 'z': 5}, GradientDescent(F1, point, num_steps=100), places=4)


if __name__ == '__main__':
  unittest.main()
