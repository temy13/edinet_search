from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import json
import helper
conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
import copy
SIZE = 10

def normal_search(_bool, offset):
    es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
    body_ = {
	"from":0,
	#"from":offset,
	"size":SIZE,
	"query": {
	  "bool":_bool
	},

        "aggs": {
          "top_tags": {
            "terms": {
                "field": "filename",
                "size": 100000
            },
            "aggs": {
                "top_result_hits": {
                    "top_hits": {
                        "sort": [
                            {
                                "term": {
                                    "order": "desc"
                                }
                            }
                        ],
                        "_source": {
                            "includes": [ "filename","id","title_index","term","publisher","term_date_range","value" ]
                        },
                        "size" : 1
                    }
                }
            }
         }
      }

    }
    d = es.search(index=conf["index"], body=body_)
    print(d["hits"]["total"], sum([x["doc_count"] for x in d['aggregations']['top_tags']['buckets']]))
    hits = [x['top_result_hits']['hits']['hits'][0] for x in d['aggregations']['top_tags']['buckets']]
    result = hits#d["hits"]["hits"]
    count = len(hits)#d["hits"]["total"]
    #return count, result
    return count, result[offset:offset+SIZE]

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
	       "format": "yyyy/MM/dd",
               "relation":"WITHIN"
          }
       }
    }
    ]
    if titles:
       idx = helper.get_es_indexes(titles)
       indexes = copy.deepcopy(idx)
       for i in idx:
           indexes.extend(helper.TITLES_SUB_INDEXES[i])
       filters.append({
        "terms": {
            "title_index": [str(i) for i in indexes]
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
        "title_index":row["_source"]["title_index"],
        "filename":row["_source"]["filename"]
                 # "title1":row["_source"]["title1"], "title2":row["_source"]["title2"], "title3":row["_source"]["title3"], "title4":row["_source"]["title4"], "title5":row["_source"]["title5"]
	} for row in result]
    return count, result
