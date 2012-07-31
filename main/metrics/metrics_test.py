from main.io.signal import UNKNOWN
from main.metrics import metrics

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'

import unittest
import mox

class MetricsTestCase(mox.MoxTestBase):

  def testTransform(self):
    self.assertEqual(0, metrics.Transform(0, 2))
    self.assertEqual(0, metrics.Transform(-10, 3))
    self.assertEqual(3, metrics.Transform(100, 3))
    self.assertEqual(2, metrics.Transform(200000, 2))
    self.assertEqual(2, metrics.Transform(67, 2))
    self.assertEqual(1, metrics.Transform(66, 2))
    self.assertEqual(2, metrics.Transform(51, 3))
    self.assertEqual(0, metrics.Transform(1, 3))
    self.assertEqual(0, metrics.Transform(24.7, 3))
    self.assertEqual(0, metrics.Transform(33, 2))

  def testEval(self):
    scores1 = [3, 2, 2]
    scores2 = [v % 3 for v in range(10)]
    values2 = [v % 3 for v in range(10)]
    self.mox.StubOutWithMock(metrics, 'EvalPerQuestion')
    metrics.EvalPerQuestion(scores1, extra_filter=mox.IgnoreArg(), only_questions=[0, 2]).AndReturn(
        [3, UNKNOWN, 2, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN])
    metrics.EvalPerQuestion(scores2, extra_filter=mox.IgnoreArg(), only_questions=None).AndReturn(values2)
    # Switch from record mode to replay mode
    self.mox.ReplayAll()
    self.assertAlmostEqual(2.5, metrics.Eval(scores1, only_questions=[0, 2]))
    self.assertAlmostEqual(.9, metrics.Eval(scores2))


if __name__ == '__main__':
  unittest.main()

