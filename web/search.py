#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from elasticsearch import Elasticsearch
import sys

server = "http://localhost"
es = Elasticsearch(server)
query = "langs:python|java -web ~#$% 数据库设计"


def extract(s:str) -> dict:
    s = re.sub(r'[%#@!$~]+', " ", s)
    s = re.sub(r'\s*\|\s*', "|", s)
    # remove space with around |
    s = re.sub(r"\s+", " ", s)
    # remove repeat space
    l = s.split(" ")
    d = {}
    for i in l.copy():
        if ":" in i:
            l.remove(i)
            key, value = i.split(":", 1)
            if key in d:
                d[key] += f" {value}"
            else:
                d[key] = value
    t = ""
    for i in l:
        t = f"{t} {i}"
    t.strip()
    d['query'] = t
    print(d)
    return d


def search(query: str, page=1,getforked=True) -> dict:
    d = extract(query)
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "function_score":
                            {"query":
                                {"simple_query_string": {
                                    "query": d['query'],
                                    "fields": ['name^3', "description"],
                                    "default_operator": "AND"
                                }
                                }
                                
                                , "script_score": {
                                "script": {
                                    "source": "1+Math.log(2 + doc['forks'].value+doc['stars'].value+doc['watchers'].value)"
                                }
                            }
                            }
                    }
                ]
                # , "filter": [{
                # "match_phrase_prefix": {
                #     "name":{
                #         "query":"n"
                #         ,"max_expansions":1000
                #     }
                # }
                
                #     "simple_query_string": {
                #         "query": d['langs'],
                #         "fields": ['langsuages.nodes.name'],
                #         "default_operator": "AND"
                #     }
                # }
                # ]
                # ,"must_not":[
                #     {
                #         "match":{"name":"python"}
                #     }
                # ]
                #
            }
            # ,
            #  "highlight": {
            #      "fields": {
            #          "name": {},
            #          "description": {}
            #      }
            #  }
        }
        , "highlight": {
            "fields": {
                "name": {},
                "description": {},

            },
            "boundary_max_scan": 1000,
            "boundary_chars": ""

        }
    }

    if not getforked:
        body['query']['bool']['filter'] = [
            {
                # "match_phrase_prefix": {
                #     "name":{
                #         "query":"n"
                #         ,"max_expansions":1000
                #     }
                # }
                "term":{
                    "isFork":False
                }
            
            }
        ]
    # langs filter
    d:dict
    # if "langs" in d:
    #     d.pop("langs")
    if "langs" in d:
        if not "filter" in body['query']['bool']:
            body['query']['bool']['filter'] = [
                {
                    # "match_phrase_prefix": {
                    #     "name":{
                    #         "query":"n"
                    #         ,"max_expansions":1000
                    #     }
                    # }
                    
                    "simple_query_string": {
                        "query": d['langs'],
                        "fields": ['langs'],
                        # "term":{
                        #     "langs":[d['langs']]
                        # },
                        #
                        "default_operator": "AND"
                    }
                }
            ]
        else:
            body['query']['bool']['filter'].append(
                {
                    "simple_query_string": {
                        "query": d['langs'],
                        "fields": ['langs'],
                        "default_operator": "AND"
                    }
                }
            
            )
        if "langs" in body['highlight']["fields"]:
            pass
        else:
            body['highlight']["fields"]['langs'] = {}
    
    res = es.search(index="repo",
                    body=body, size=10, from_=(page - 1) * 10)
    print(res)
    return res


if __name__ == '__main__':
    search(query,getforked=False)
