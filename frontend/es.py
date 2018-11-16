from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import db
import json

conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
 
es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))


def search(query, t_from="", t_to="", offset=0, titles=[]):
    t_from = "1980/01/01" if not t_from else t_from
    t_to = "2030/12/31" if not t_to else t_to
    q_titles = str(tuple(titles)).replace(',)',')')
    offset = int(offset)
    filters =[{ 
	"wildcard": {
	  "value":{
	     "value":"*"+query+"*"
	  }
        }
    },{
	"range": {
          "term_date_range": {
	     "gte":t_from,
             "lte":t_to,
	     "format": "yyyy/MM/dd"
          }
        }
    }
    ]
    _bool = {"filter":filters}
    if titles:
       shoulds = [{
        "terms": {
            "title%s" % str(n): titles
        } } for n in range(1,6)]
       _bool["should"] = shoulds
       _bool["minimum_should_match"] = 1
    body_ = {
	"from":0,
	"size":3000,
	"query": {
	   "bool":_bool
	}
    }
    result = []
    s_size = 1
    s_id = None
    s_time="2m"
    while(s_size):
      d = es.search(index=conf["index"], body=body_, scroll=s_time) if not s_id else es.search(scroll_id=s_id, scroll=s_time,request_timeout=150)
      s_id = data['_scroll_id']
      s_size = len(data['hits']['hits'])
      result.extend(d["hits"]["hits"])
      
    result = [{
	"value":row["_source"]["value"], "publisher":row["_source"]["publisher"], "term":row["_source"]["term"], 
	"term_from":row["_source"]["term_date_range"]["gte"], "term_to":row["_source"]["term_date_range"]["lte"],
        "title1":row["_source"]["title1"], "title2":row["_source"]["title2"], "title3":row["_source"]["title3"], "title4":row["_source"]["title4"], "title5":row["_source"]["title5"]
	} for row in result]
    result = result_filter(result)
    return result

def result_filter(result):
    r = []
    check = set([])
    #自分より下が既に存在していたらスルー
    for n in [5, 4, 3, 2, 1]:
        for d in [r for r in result if r["title" + str(n)]]:
            t = False

            k = d["publisher"] + d["term"]
            check.add(k)
            if k not in check:
                t = True

            for i in range(1,6):
                k += d["title" + str(i)]
                if k not in check:
                    t = True
                check.add(k)
            if t:
                r.append(d)
    return r



#print(len(search("エレクトロニクス")))
#search("エレクトロニクス", titles=["第一部ファンド情報"])
#print(len(search("表紙")))
print(len(search("一般")))
#search("表紙", titles=["表紙"])
#search("エレクト")
