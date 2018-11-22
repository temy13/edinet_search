from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import json

conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
 
SIZE = 10

def normal_search(_bool, offset):
    es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
    body_ = {
	"from":offset,
	"size":SIZE,
	"query": {
	  "bool":_bool
	}
    }
    d = es.search(index=conf["index"], body=body_)
    result = d["hits"]["hits"]
    count = d["hits"]["total"]
    return count, result

def scroll_search(_bool, offset):
    es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
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
      d = es.search(index=conf["index"], body=body_, scroll=s_time) if not s_id else es.scroll(scroll_id=s_id, scroll=s_time)
      s_id = d['_scroll_id']
      s_size = len(d['hits']['hits'])
      result.extend(d["hits"]["hits"])
      if len(result) > (offset + SIZE):
        break
    count = d["hits"]["total"]
    return count, result[offset:offset+SIZE]
    


def search(query, t_from="", t_to="", offset=0, titles=[]):
    t_from = "1980/01/01" if not t_from else t_from
    t_to = "2030/12/31" if not t_to else t_to
    q_titles = str(tuple(titles)).replace(',)',')')
    offset = int(offset)
    filters =[
    #{ 
    #	"wildcard": {
    #	  "value":{
    #	     "value":"*"+query+"*"
    #	  }
    #   }
    #},
    {
	"match_phrase":{
		"value":query
	}
    },
    {
    	"range": {
           "term_date_range": {
            "gte":t_from,
            "lte":t_to,
	     "format": "yyyy/MM/dd"
          }
       }
    }
    ]
    if titles:
       filters.append({
        "terms": {
            "key": titles
        }})
       #_bool["should"] = shoulds
       #_bool["minimum_should_match"] = 1
    _bool = {"filter":filters}
    if offset < 99900:
      count, result = normal_search(_bool, offset)
    else:
      count, result = scroll_search(_bool, offset)
    result = [{
	"value":row["_source"]["value"], "publisher":row["_source"]["publisher"], "term":row["_source"]["term"], 
	"term_from":row["_source"]["term_date_range"]["gte"], "term_to":row["_source"]["term_date_range"]["lte"],
        "key":row["_source"]["key"]
                 # "title1":row["_source"]["title1"], "title2":row["_source"]["title2"], "title3":row["_source"]["title3"], "title4":row["_source"]["title4"], "title5":row["_source"]["title5"]
	} for row in result]
    return count, result

