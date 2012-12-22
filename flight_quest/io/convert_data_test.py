import unittest
import datetime
from flight_quest.io import convert_data

class ConvertTimeTest(unittest.TestCase):

  def testParseTime(self):
    t0 = datetime.datetime(2012, 12, 10, 0, 0)
    self.assertEqual(0, convert_data.ParseDateTime('12/10/12 00:00', t0))
    self.assertEqual(10, convert_data.ParseDateTime('12/10/12 00:10', t0))
    self.assertEqual(600, convert_data.ParseDateTime('12/10/12 10:00', t0))
    self.assertEqual(671, convert_data.ParseDateTime('12/10/12 11:11', t0))
    self.assertEqual(-1000, convert_data.ParseDateTime('12/10/12 11:111', t0))
    self.assertEqual(-1000, convert_data.ParseDateTime('bla', t0))

  def testParseLine(self):
    t0 = datetime.datetime(2012, 11, 15, 0, 0)
    desc = 'Nothing'
    self.assertEqual(-1000, convert_data.ParseNewEstimationTime(desc, 'EGA', t0))
    desc = 'ERD- Old=11/15/12 10:07 New=11/15/12 19:15, AEQP- New=BE40'
    self.assertEqual(-1000, convert_data.ParseNewEstimationTime(desc, 'EGA', t0))
    desc = 'EGA- Old=11/15/12 06:07 New=11/15/12 10:15, ERA- New=BE40'
    self.assertEqual(-1000, convert_data.ParseNewEstimationTime(desc, 'ERA', t0))
    self.assertEqual(615, convert_data.ParseNewEstimationTime(desc, 'EGA', t0))
    desc = 'EGA- Old=11/15/12 06:07 ERA- New=11/15/12 12:15'
    self.assertEqual(735, convert_data.ParseNewEstimationTime(desc, 'ERA', t0))
    self.assertEqual(-1000, convert_data.ParseNewEstimationTime(desc, 'EGA', t0))