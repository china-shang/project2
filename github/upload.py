#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import itertools
from datahandler import Model,load
from elasticsearch import Elasticsearch, ElasticsearchException


#ec = Elasticsearch("https://search-elasticsearch-msmewlsyqwsf72nkto4atpvqrq.ap-northeast-1.es.amazonaws.com/")
ec = Elasticsearch("http://localhost")

def create_index():
    ec.indices.delete(index = "repo")
    body = {
        "settings":{
            "analysis":{
                "analyzer":{
                    "myanalyzer":{
                        "tokenizer":"ik_smart",
                        #"tokenizer":"smartcn_tokenizer",
                        "filter":["stemmer"]
                    }
                }
            }
        }
    }
    res = ec.indices.create(index = "repo", body = body)
    # print(res)
    
    body = {
        "properties":{
            "description":{
                "type":"text",
                "analyzer":"myanalyzer",
                "search_analyzer":"myanalyzer",
            },
            
            "name":{
                "type":"text",
                "analyzer":"myanalyzer",
                "search_analyzer":"myanalyzer",
            }
            ,"langs": {
                "fields": {
                    "text": {
                        "type": "text",
                        "analyzer":"myanalyzer",
                        "search_analyzer":"myanalyzer",
                    }
                },
                "type": "text"
            }
            ,"license": {
                        "fields": {
                            "text": {
                                "analyzer":"myanalyzer",
                                "search_analyzer":"myanalyzer",
                                "type": "text"
                            }
                        },
                        "type": "text"
                    }
            , "updatedAt": {
                        "type": "text"
                    }
        }
    }
    print(ec.indices.put_mapping(doc_type = "_doc", body = body, index = "repo"))

def add_one(repos:list):
    """
    add one at a time
    """
    for i in repos:
        res = ec.update(index = "repo",id = i['url'],  doc_type = "_doc", body = {"doc":i, "doc_as_upsert":True})
        print(res)



def add_list(repos:list):
    """
    add multiple item to ec once
    """
    def _gen_index(url=""):
        return {"update":{
            "_id":url,
            #"doc_as_upsert":True
        }
        }
    
    if not (repos and len(repos)>0):
        return
    l1=_gen_index()
    #l1 = [{"index":{}}] * len(repos)
    body = []
    #for i in zip(l1, repos):
    #body.extend(i)
    for i in repos:
        prefix=_gen_index(i['url'])
        body.extend([prefix, {"doc":i, "doc_as_upsert":True}])
    
    while True:
        try:
            res = ec.bulk(index = "repo",doc_type = "_doc",body = body)
        except Exception as e:
            print(e)
        else :
            return len(repos)
            break


# create_index()

count=0
files=glob.glob("./data/repos15*")
for file in files:
    with open(file) as fp:
        l=load(fp.read())
        # for i in l:
        #     m=Model(data=i,src="gitee")
        ms=[Model(data=i,src="github") for i in l ]
        t=add_list(ms)
        count+=t
        print(f"success {count}")
        # print(m)



files=glob.glob("../data/repos15*")
for file in files:
    with open(file) as fp:
        l=load(fp.read())
        # for i in l:
        #     m=Model(data=i,src="gitee")
        ms=[Model(data=i,src="github") for i in l ]
        t=add_list(ms)
        count+=t
        print(f"success {count}")
        # print(m)



