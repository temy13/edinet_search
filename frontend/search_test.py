import server
import unittest
from datetime import datetime as dt
import datetime
from glob import glob
import db

#backend/data/E14394/Xbrl_Search_20181125_211001.zip
#unittest.main(warnings='ignore')
class TestSearch(unittest.TestCase):
  
  def test_normal(self):
    for q in ["【表紙】","一部","会計事務所"]:
      count, rdata = server.search(q)
      filenames = db.get_all_filenames()
      print("filenames",len(filenames))
      self.assertEqual(10, len(rdata))
      c = [set([]), set([]), set([]), set([])]
      for path in glob("backend/data/*/*/*/*/*/*.htm"):
        with open(path) as f:
          s = f.read()
          fn = path.split("/")[-1]
          zipfn = "/".join(path.split("/")[:4]) + "zip"
          if not zipfn in filenames:
            print(zipfn)
            continue
          if s.find(q) < 0:
            continue
          if fn.startswith("0000"):
            c[0].add(zipfn)
          elif fn.startswith("01"):
            c[1].add(zipfn)
          elif fn.startswith("02"):
            c[2].add(zipfn)
          else:
            c[3].add(zipfn)
      print(q, len(c[0]), len(c[1]), len(c[2]), len(c[3]))
      self.assertEqual(len(c[0] | c[1] | c[2] | c[3]), count)

      count, rdata = server.search(q, titles=["表紙"])
      self.assertEqual(len(c[0]), count)

      count, rdata = server.search(q, titles=["第一部ファンド情報"])
      self.assertEqual(len(c[1]), count)
      
      count, rdata = server.search(q, titles=["第二部投資法人の詳細情報"])
      self.assertEqual(len(c[2]), count)
  
  
  
  def test_with_dt(self):
    return
    for q in ["会計事務所"]:
      count, rdata = server.search(q, t_from="2014/01/01",t_to="2017/12/31")
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
    return
    for q in ["会計事務所"]:
      count, rdata = server.search(q, t_from="2014/01/01",t_to="2017/12/31")
      mod = count % 10
      offset = count - mod
      count2, rdata2 = server.search(q, offset=offset, t_from="2014/01/01",t_to="2017/12/31")
      self.assertEqual(count, count2)
      self.assertEqual(mod, len(rdata2))

if __name__ == "__main__":
    unittest.main(warnings='ignore')
    #unittest.main()


