from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import db
import sys
import re
conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
import etl
import uuid
from helper import *
import helper
es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
n = 0
LIMIT = 1000

def g_title_indexes(titles):
    l = [es_title_index(t) for t in titles]
    #52番と58番は同じ値になるので特別処理
    idxes = [i for i, x in enumerate(l) if x == 52]
    for i in idxes:
      if i <= 0:
        continue
      if 0 <= l[i-1] <= 51: l[i] = 52
      if 52 <= l[i-1] <= 57: l[i] = 58
    idxes = []
    re_titles = []
    for i in range(len(l)):
      if i == 0 and l[i] <= l[i+1]:
        idxes.append(l[i])
        re_titles.append(titles[i])
      elif i == len(l)-1 and l[i-1] < l[i]:
        idxes.append(l[i])
        re_titles.append(titles[i])
      elif l[i-1] < l[i] <= l[i+1]:
        idxes.append(l[i])
        re_titles.append(titles[i])
    if len(l)-len(idxes):
      print(len(l)-len(idxes), l, len(l))
    return re_titles, idxes


def ex_parse(html, fn):
    #titles = re.findall("<h\d[\s\S]*?>.*?<\/h\d>", html)
    #titles = [x for x in re.findall("<h1(.|\s)*?>(.|\s)*?<\/h1>", html)]

    divs = [x for x in re.split("<h\d(.|\s)*?>", html) if x and "</h" in x]
    titles = []
    for div in divs:
        t_idx = div.find("</h")
        title = div[:t_idx]
        #title = title_minimum_normalize(title)
        t_v = title_normalize(title)
        if t_v in helper._titles:
            titles.append(title)
    if title_normalize(titles[0]) != "表紙":
      if html.find("【表紙】") >= 0:
        titles.insert(0, "【表紙】")

    #titles.append("独立監査人の監査報告書")
    #titles.append("独立監査人")
    html = etl.extract_html(html)
    text = etl.parse(html)
    d = {}
    f_idx = 0
    t_idx = 0
    titles, title_indexes = g_title_indexes(titles)
    for n in range(len(titles)-1):
        f_idx = text.find(etl.parse(titles[n]), t_idx)
        t_idx = text.find(etl.parse(titles[n+1]), f_idx)
        subtext = text[f_idx:t_idx]
        if not subtext:
          print(titles[n], f_idx, t_idx)
        i = title_indexes[n]
        d[i] = subtext
    f_idx = text.find(titles[-1])
    subtext = text[f_idx:-1]
    d[title_indexes[-1]] = subtext
    if not subtext:
      print(titles[n], f_idx, len(text))
    insert_es(d, fn)





def insert_to_es(fn):
     data = db.get_data_by_fn(fn)
     if not data:
         print("NODATA", fn)
         #continue
         return
     ex_parse(data[0]["origin"], fn)


def connection(data, i):
    target_title_indexes = [i] + helper.TITLES_SUB_INDEXES[i]
    return "".join([data[idx] for idx in target_title_indexes if idx in data])


def insert_es(data, fn):
    datas = []
    for i,v in data.items():
        k = get_title_from_index(i)
        v = connection(data, i)
        row = db.get_meta(fn)
        d = {
	   "value":v,
	   "title_index":i,
	   #"title":k,
	   "term":row["term"],
	   "publisher":etl.parse(row["publisher"]),
           "filename":fn,
	   "term_date_range": {
	     "gte":row["term_from"],
	     "lte":row["term_to"]
	      }
        }
        if not v:
          print("NOV", i, k, fn)
        _id = uuid.uuid1()
        datas.append({'_id':_id.int, '_op_type':'create','_index':conf["index"],'_type':conf["doc_type"],'_source':d})
        #db.insert_target(code="", filename=fn, value=d["value"], key=d["key"], term=d["term"], term_from=row["term_from"], term_to=row["term_to"], publisher=row["publisher"])
    helpers.bulk(client=es,actions=datas,refresh=True,chunk_size=1000,request_timeout=150)
    #print("inserted", len(data))


def main():

    filenames = db.get_all_filenames()
    for i, fn in enumerate(filenames):
        print("%s/%s" % (i, len(filenames)),end="\r")
        data = db.get_data_by_fn(fn)
        if not data:
            continue
        ex_parse(data[0]["origin"], fn)
    print("----")
#main()
