from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import db
import sys
import scrape
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


def ex_parse(html, fn):
    #titles = re.findall("<h\d[\s\S]*?>.*?<\/h\d>", html)
    #titles = [x for x in re.findall("<h1(.|\s)*?>(.|\s)*?<\/h1>", html)]
    divs = [x for x in re.split("<h\d(.|\s)*?>", html) if x and "</h" in x]
    titles = []
    for div in divs:
        t_idx = div.find("</h")
        t = div[:t_idx]
        t_v = title_normalize(t)
        if t_v in helper._titles:
            titles.append(t)
    titles.append("監査報告書")
    html = etl.extract_html(html)
    text = etl.parse(html)
    d = {}
    for n in range(len(titles)-1):
        f_idx = text.find(titles[n])
        t_idx = text.find(titles[n+1])
        subtext = text[f_idx:t_idx]
        d[title_normalize(titles[n])] = subtext
    f_idx = text.find(titles[-1])
    subtext = text[f_idx:-1]
    d[title_normalize(titles[-1])] = subtext
    insert_es(d, fn)

#def main():
#    df = scrape.get_codes()
#
#    for index, item in df.iterrows():
#        code = item["code"]
#        filenames = db.get_filenames(code)
#        for fn in filenames:
#            data = db.get_data_by_fn(fn)
#            if not data:
#                continue
#            ex_parse(data[0]["origin"], fn)
#    print("----")


def insert_to_es(fn):
     data = db.get_data_by_fn(fn)
     if not data:
         #continue
         return
     ex_parse(data[0]["origin"], fn)


def connection(data, k):
    targets = [k] + helper._titles_sub[k]
    return "".join([data[t] for t in targets if t in data])


def insert_es(data, fn):
    datas = []
    for k,v in data.items():
        v = connection(data, k)
        row = db.get_meta(fn)
        d = {
	   "value":v,
	   "title":k,
	   "term":row["term"],
	   "publisher":etl.parse(row["publisher"]),
           "filename":fn,
	   "term_date_range": {
	     "gte":row["term_from"],
	     "lte":row["term_to"]
	      }
        }
        _id = uuid.uuid1()
        datas.append({'_id':_id.int, '_op_type':'create','_index':conf["index"],'_type':conf["doc_type"],'_source':d})
        #db.insert_target(code="", filename=fn, value=d["value"], key=d["key"], term=d["term"], term_from=row["term_from"], term_to=row["term_to"], publisher=row["publisher"])
    helpers.bulk(client=es,actions=datas,refresh=True,chunk_size=1000,request_timeout=150)
    print("inserted", len(datas) )
#main()
