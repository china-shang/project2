#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        
        {'took': 12, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
         'hits': {'total': 1212, 'max_score': 29.5795, 'hits': [
             {'_index': 'repo', '_type': '_doc', '_id': 'LTVuK2cBmMsYjO0YHcip', '_score': 29.5795,
              '_source': {'name': 'java', 'url': 'https://github.com/SirEOF/java',
                          'description': 'Rosette API Client Library for Java', 'updatedAt': '2018-01-01T20:27:57Z',
                          'projectsUrl': 'https://github.com/SirEOF/java/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Java'}, {'name': 'Python'}, {'name': 'Shell'}]},
                          'stargazers': {'totalCount': 0}, 'watchers': {'totalCount': 1}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'], 'name': ['<em>java</em>'],
                            'description': ['Rosette API Client Library for <em>Java</em>']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'VS1sK2cBmMsYjO0YAOau', '_score': 29.324688,
              '_source': {'name': 'java', 'url': 'https://github.com/SirEOF/java',
                          'description': 'Rosette API Client Library for Java', 'updatedAt': '2018-01-01T20:27:57Z',
                          'projectsUrl': 'https://github.com/SirEOF/java/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Java'}, {'name': 'Python'}, {'name': 'Shell'}]},
                          'stargazers': {'totalCount': 0}, 'watchers': {'totalCount': 1}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'], 'name': ['<em>java</em>'],
                            'description': ['Rosette API Client Library for <em>Java</em>']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'xjBsK2cBmMsYjO0YmCgs', '_score': 8.48684,
              '_source': {'name': 'WebProgram', 'url': 'https://github.com/cryptomanic/WebProgram',
                          'description': 'A simple web application using HTML, CSS and Python.',
                          'updatedAt': '2016-02-01T14:23:46Z',
                          'projectsUrl': 'https://github.com/cryptomanic/WebProgram/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'CSS'}, {'name': 'HTML'}]}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                            'description': ['A simple <em>web</em> application using <em>HTML</em>, CSS and Python.']}},
             {'_index': 'repo', '_type': '_doc', '_id': '-DBsK2cBmMsYjO0YmCgs', '_score': 8.399796,
              '_source': {'name': 'WebProgram', 'url': 'https://github.com/cryptomanic/WebProgram',
                          'description': 'A simple web application using HTML, CSS and Python.',
                          'updatedAt': '2016-02-01T14:23:46Z',
                          'projectsUrl': 'https://github.com/cryptomanic/WebProgram/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'CSS'}, {'name': 'HTML'}]}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                            'description': ['A simple <em>web</em> application using <em>HTML</em>, CSS and Python.']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'dzZuK2cBmMsYjO0YV40v', '_score': 8.041086,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/hanmichael/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2017-04-08T08:16:09Z',
                          'projectsUrl': 'https://github.com/hanmichael/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]},
                          'stargazers': {'totalCount': 0},
                          'watchers': {'totalCount': 1}}, 'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                                                                        'description': [
                                                                            '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'CzZuK2cBmMsYjO0YWJEn', '_score': 8.041086,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/hanmichael/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2017-04-08T08:16:09Z',
                          'projectsUrl': 'https://github.com/hanmichael/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]},
                          'stargazers': {'totalCount': 0},
                          'watchers': {'totalCount': 1}}, 'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                                                                        'description': [
                                                                            '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'ujhuK2cBmMsYjO0Y3omv', '_score': 8.041086,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/CaryLeo7/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2017-01-14T14:18:03Z',
                          'projectsUrl': 'https://github.com/CaryLeo7/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]},
                          'stargazers': {'totalCount': 0},
                          'watchers': {'totalCount': 0}}, 'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                                                                        'description': [
                                                                            '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'zzhuK2cBmMsYjO0Y3omv', '_score': 8.041086,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/CaryLeo7/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2017-01-14T14:18:03Z',
                          'projectsUrl': 'https://github.com/CaryLeo7/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]},
                          'stargazers': {'totalCount': 0},
                          'watchers': {'totalCount': 0}}, 'highlight': {'languages.nodes.name': ['<em>Python</em>'],
                                                                        'description': [
                                                                            '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'aThuK2cBmMsYjO0YzEyN', '_score': 8.041086,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/id0o0bi/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2016-12-22T14:40:39Z',
                          'projectsUrl': 'https://github.com/id0o0bi/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'], 'description': [
                  '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}},
             {'_index': 'repo', '_type': '_doc', '_id': 'cy5sK2cBmMsYjO0YMqdm', '_score': 8.039774,
              '_source': {'name': 'python-goose', 'url': 'https://github.com/mack007liu/python-goose',
                          'description': 'Html Content / Article Extractor, web scrapping lib in Python',
                          'updatedAt': '2015-04-08T08:32:05Z',
                          'projectsUrl': 'https://github.com/mack007liu/python-goose/projects', 'forkCount': 0,
                          'languages': {'nodes': [{'name': 'Python'}, {'name': 'HTML'}]}},
              'highlight': {'languages.nodes.name': ['<em>Python</em>'], 'description': [
                  '<em>Html</em> Content / Article Extractor, <em>web</em> scrapping lib in Python']}}]}}
        
        query: str = data['query']
        page: int = data['page']
        res = {}
        
        # query = "lang:python|java web html | 商城)"
        if not query:
            query = "shop"
        resp = search(query, page=page)
        res = {}
        res['total'] = resp['hits']['total']
        res['repo'] = []
        for i in resp['hits']['hits']:
            if 'description' in i['highlight']:
                i['_source']['desr'] = i['highlight']['description'][0]
            else:
                i['_source']['desr'] = i['_source']['description']
            
            if 'name' in i['highlight']:
                i['_source']['name'] = i['highlight']['name'][0]
            else:
                i['_source']['name'] = i['_source']['name']
            lang = i['_source']['languages']['nodes']
            i['_source']['lang'] = []
            if 'languages.nodes.name' in i['highlight']:
                i['_source']['lang'].extend(i['highlight']['languages.nodes.name'])
            # else:
            #     i['_source']['lang']=i['_source']['languages']['nodes'][0]['name']
            for j in lang:
                if len(i['_source']['lang'])>3:
                    break
                if not inhightlight(j['name'], i['_source']['lang']):
                    i['_source']['lang'].append(j['name'])

            if len(i['_source']['lang'])==0:
                i['_source']['lang']=["unknown"]
            
            
            try:
                i['_source']['star'] = i['_source']['stargazers']['totalCount']
            except KeyError as e:
                print(e)
                i['_source']['star'] = 0
            try:
                i['_source']['watch'] = i['_source']['watchers']['totalCount']
            except KeyError as e:
                print(e)
                i['_source']['watch'] = 0
            i['_source']['user'] = i['_source']['url'].rsplit("/", 2)[-2]
            i['_source']['src'] = "Github"
            i['_source']['license'] = "GPL3"
            i['_source']['fork'] = i['_source']['forkCount']
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
            repos=res['repo'],
            page={"start": start, "end": end, "cur": page, "url": range(start, end + 2),
                  "more":page!=all}
        )
        return web.Response(body=s, content_type="text/html")
    
    async def home(self, req: web.Request):
        hander = Hander()
        res = hander.get({
            "query": "sdfj sdjf",
            "page": 1
        })
        tmp = env.get_template("main1.html")
        with open("main.html", "w") as fp:
            s = tmp.render(repos=res['repo'],
                           page={"start": 4, "end": 11, "cur": 8, "url": ['1', '3', '4', '5']}
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
    app.add_routes([web.get('/home', t.home),
                    web.get('/', t.search)])
    
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
        "query": "sdfj sdjf",
        "page": 1
    })
    tmp = env.get_template("repos_li.html")
    # print(tmp.render(repos=res['repo'] ))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    
    test1()
