import server
import unittest
from datetime import datetime as dt
import datetime

class TestSearch(unittest.TestCase):
  
  def test_normal(self):
    count, rdata = server.search("会計事務所")
    #存在している
    #ここで全部のファイルチェック
    self.assertEqual(991, count)
    self.assertEqual(10, len(rdata))
    #表紙
    #1部
    #2部
  
  def test_with_dt(self):
    count, rdata = server.search("会計事務所", t_from="2014/01/01",t_to="2017/12/31")
    #存在している
    self.assertEqual(952, count)
    self.assertEqual(10, len(rdata))
    froms = sorted([dt.strptime(d["term_from"], '%Y/%m/%d') for d in rdata])
    tos = sorted([dt.strptime(d["term_to"], '%Y/%m/%d') for d in rdata])
    f = datetime.datetime.strptime("2014/01/01", '%Y/%m/%d')
    t = datetime.datetime.strptime("2017/12/31", '%Y/%m/%d')
    self.assertTrue(f <= froms[0] <= t)
    self.assertTrue(f <= froms[-1] <= t)
    self.assertTrue(f <= tos[0] <= t)
    self.assertTrue(f <= tos[-1] <= t)
  
  def test_offset(self):
    count, rdata = server.search("会計事務所", offset=950, t_from="2014/01/01",t_to="2017/12/31")
    self.assertEqual(952, count)
    self.assertEqual(2, len(rdata))

if __name__ == "__main__":
    unittest.main()
