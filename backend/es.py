from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import db

conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
 
es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
n = 0
LIMIT = 1000
while(True):
    data = db.get_all_values(limit=LIMIT, offset=n * LIMIT)
    if not data:
        break
    datas = []
    for row in data:
        d = {
	   "value":row["value"],
	   "title1":row["title1"],	
	   "title2":row["title2"],	
	   "title3":row["title3"],	
	   "title4":row["title4"],	
	   "title5":row["title5"],
	   "term":row["term"],
	   "publisher":row["publisher"],
	   "term_date_range": {
	     "gte":row["term_from"],
	     "lte":row["term_to"]
	   }
        }
        datas.append({'_id':row["id"], '_op_type':'create','_index':conf["index"],'_type':conf["doc_type"],'_source':d})
     
    helpers.bulk(client=es,actions=datas,refresh=True,chunk_size=1000,request_timeout=150)
    print("inserted", n, n*LIMIT+len(datas) )
    n += 1

