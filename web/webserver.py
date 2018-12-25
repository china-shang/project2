#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
realpath=os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0,realpath)

import asyncio
import jinja2
from aiohttp import web

from logger import get_logger
from web.search import search

logger = get_logger(__name__)

server_addr = "0.0.0.0"
server_port = 8080


def inhightlight(s: str, l: list):
    l1 = []
    for i in l:
        i: str
        t = i.replace("<em>", "")
        t = t.replace("</em>", "")
        t = t.lower()
        l1.append(t)
    
    for i in l1:
        if s.lower() in i:
            return True
    return False


loader = jinja2.FileSystemLoader("/home/zh/.WebstormProjects/untitled1")
env = jinja2.Environment(loader=loader)


class Hander(object):
    def get(self, data: dict):
        
        query: str = data['query']
        page: int = data['page']
        res = {}
        
        # query = "lang:python|java web html | 商城)"
        if not query:
            query = "shop"
        resp = search(query, page=page)
        res = {}
        res['took']=resp['took']
        res['total'] = resp['hits']['total']
        res['repo'] = []
        for i in resp['hits']['hits']:
            if 'description' in i['highlight']:
                i['_source']['desr'] = i['highlight']['description'][0]
            else:
                i['_source']['desr'] = i['_source']['description']

            #if len(i['_source']['desr']) == 120:
                #i['_source']['desr'] += "..."
            
            if 'name' in i['highlight']:
                i['_source']['name'] = i['highlight']['name'][0]
            else:
                i['_source']['name'] = i['_source']['name']
            lang = i['_source'].get("langs",[])
            i['_source']['lang'] = []
            if 'langs' in i['highlight']:
                i['_source']['lang'].extend(i['highlight']['langs'])
            # else:
            #     i['_source']['lang']=i['_source']['languages']['nodes'][0]['name']
            for j in lang:
                if len(i['_source']['lang'])>3:
                    break
                if not inhightlight(j, i['_source']['lang']):
                    i['_source']['lang'].append(j)

            if len(i['_source']['lang'])==0:
                i['_source']['lang']=["unknown"]
                
            if i['_source'].get('license',None) and len(i['_source']['license'])==0:
                i['_source']['license']=None
            
            
            try:
                i['_source']['star'] = i['_source']['stars']
            except KeyError as e:
                print(e)
                i['_source']['star'] = 0
            try:
                i['_source']['watch'] = i['_source']['watchers']
            except KeyError as e:
                print(e)
                i['_source']['watch'] = 0
            
            s:dict
            # s.setdefault("license",s.get())
            # i['_source'].set
            i['_source']['user'] = i['_source']['url'].rsplit("/", 2)[-2]
            # i['_source']['src'] = "Github"
            i['_source']['fork'] = i['_source']['forks']
            
            if "T" in i['_source']['updatedAt']:
                updated=i['_source']['updatedAt'].split("T")[0]
                i['_source']['updatedAt']=updated
                
            res['repo'].append(i['_source'])
        
        print(res)
        return res


class Server(object):
    def __init__(self):
        pass
    
    async def search(self, req: web.Request):
        q = req.query.getall("q")[0]
        print(f"all q={q}")
        page = int(req.query.get("page"))
        hander = Hander()
        res = hander.get({
            "query": q,
            "page": page
        })
        tmp = env.get_template("main1.html")
        # with open("main.html","w") as fp:
        #     s=tmp.render(
        #         q=q,
        #         repos=res['repo'] ,
        #                  page={"start": 1, "end": 8, "cur": 1, "url": range(1,9)}
        #                  )
        #     fp.write(s)
        # data = await req.json()
        # print(data)
        # s=""
        # with open("main.html") as f:
        #     s=f.read()
        print(f"2all q={q.split(' ')}")
        all = int(res['total'] / 10)
        start = page - 4
        if start < 1:
            start = 1
        
        end = start + 7
        if end > all:
            end = all
        
        s = tmp.render(
            q=q,
            total=res['total'], 
            took=res['took'], 
            repos=res['repo'],
            page={"start": start, "end": end, "cur": page, "url": range(start, end + 2),
                  "more":page<all}
        )
        return web.Response(body=s, content_type="text/html")
    
    async def home(self, req: web.Request):
        hander = Hander()
        res = hander.get({
            "query": "asdjfasiodfjasdlkfjas234234",
            "page": 1
        })
        tmp = env.get_template("main1.html")
        with open("main.html", "w") as fp:
            s = tmp.render(repos=res['repo'],
                           page={"start": 1, "end": 1, "cur": 1, "url": ['1', '3', '4', '5']},
                           title="main"
                           )
            fp.write(s)
        # data = await req.json()
        # print(data)
        s = ""
        with open("main.html") as f:
            s = f.read()
        return web.Response(body=s, content_type="text/html")
    
    async def repolist(self, req: web.Request):
        
        data = await req.json()
        data: dict
        tmp = env.get_template("repos_li.html")
        print(tmp.render(repos=[{"name": "name1",
                                 "user": "user1",
                                 "src": "github",
                                 "url": "www.baidu.com/name/user1",
                                 "desr": "this is description",
                                 "license": "GPL3",
                                 "star": 334,
                                 "fork": 3432,
                                 "watch": 324,
                                 "lang": "C++"
                                 },
                                {"name": "name2",
                                 "user": "user2",
                                 "src": "github",
                                 "url": "www.baidu.com/name/user2",
                                 "license": "GPL3",
                                 "star": 334,
                                 "fork": 3432,
                                 "watch": 324,
                                 "lang": "C++"
                                 }
                                ]))


async def test():
    t = Server()
    
    app = web.Application()
    app.add_routes([web.get('/', t.home),
                    web.get('/search', t.search)])
    
    runner = web.AppRunner(app)
    await runner.setup()

    svr = web.TCPSite(runner, server_addr, server_port)
    await svr.start()
    
    logger.info(f"server started at {server_addr}:{server_port}")
    f = asyncio.Future()
    await f


def test1():
    hander = Hander()
    res = hander.get({
        "query": "s",
        "page": 1
    })
    tmp = env.get_template("repos_li.html")
    # print(tmp.render(repos=res['repo'] ))


if __name__ == "__main__":
    # test1()
    # exit()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    
