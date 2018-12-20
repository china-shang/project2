import asyncio
import os
import sys
from itertools import product

import aiohttp
from bs4 import BeautifulSoup as Soup

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.basespider import BaseSpider
from gitee.session import Session
from logger import get_logger
logger = get_logger(__name__)


class Spider(BaseSpider):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }
    
    _url_prefix = "https://gitee.com/"
    
    def __init__(self, timeout=aiohttp.ClientTimeout(total=60)):
        self._timeout = timeout
        self._session = Session(headers=self.header,
                                timeout=self._timeout)
        self.name:str = ""
    
    async def fetch(self, user:str, project:bool=True)->list:
        await super().fetch("")
        if not self._session or self._session.closed:
            self._session = Session(headers=self.header,
                                    timeout=self._timeout)
        
        self.name=user
        try:
            if project:
                return await self.fetch_project()
            else:
                return await self.fetch_users()
        except aiohttp.ClientError as e:
            e.args[0]
            logger.error(f"client error {e}")
            raise e
        except Exception as e:
            logger.error(f"exception e")
            raise e
            
    
    async def fetch_project(self):
        #TODO use ajax request
        url = self._url_prefix + self.name + "/projects" + "?page={}"
        res = []
        async with self._session.get(url.format(1)) as resp:
            text = await resp.text()
            sp = Soup(text, "lxml")
            pages = self.get_pager_count(sp)
            t=sp.select("div.project")
            sp.decompose()
            res.extend(t)
            # print(pages,url.format(1))

        for i in range(2, pages + 1):
            async with self._session.get(url.format(i)) as resp:
                text = await resp.text()
                sp = Soup(text, "lxml")
                t=sp.select("div.project")
                sp.decompose()
                res.extend(sp)
        # logger.info(f"projects={res}")
        return res
    
    async def fetch_users(self):
        res = []
        res.extend(await self.fetch_followers())
        res.extend(await self.fetch_following())
        # res.extend(await self.fetch_stars())
        # res.extend(await self.fetch_watches())
        # logger.info(f"res={res}")
        return res
    
    def get_pager_count(self, sp: Soup):
        t = sp.select(".pagination > a.item")
        if len(t) < 2:
            pages = 1
        else:
            pages = int(t[-2].text)
        return pages

    async def fetch_following(self):
        url = self._url_prefix + self.name + "/following" + "?page={}"
        res = []
        async with self._session.get(url.format(1)) as resp:
            text = await resp.text()
            sp = Soup(text, "lxml")
            # res.extend(sp)
            pages = self.get_pager_count(sp)
            sp.decompose()
            # print(pages,url.format(1))
    
        for i in range(2, pages + 1):
            async with self._session.get(url.format(i)) as resp:
                text = await resp.text()
                sp = Soup(text, "lxml")
                res.extend(sp.select(".user-list-item .header a"))
                sp.decompose()
        return res

    async def fetch_followers(self):
        url = self._url_prefix + self.name + "/followers" + "?page={}"
        res = []
        async with self._session.get(url.format(1)) as resp:
            text = await resp.text()
            sp = Soup(text, "lxml")
            res.extend(sp.select(".user-list-item .header a"))
            pages = self.get_pager_count(sp)
            sp.decompose()
        
        for i in range(2, pages + 1):
            async with self._session.get(url.format(i)) as resp:
                text = await resp.text()
                sp = Soup(text, "lxml")
                res.extend(sp.select(".user-list-item .header a"))
                sp.decompose()
        return res
    
    async def fetch_stars(self):
        pass
    
    async def fetch_watches(self):
        pass
    
    async def close(self):
        await self._session.close()
    
    def closed(self):
        return self._session.closed

async def test():
    # s=Session()
    # async with s.get("https://www.baidu.com") as resp:
    #     t=await resp.text()
    #     print(t)
        
    import requests
    resp=requests.get("https://gitee.com/")
    print(resp.text)
    spider = Spider()
    res=await spider.fetch("pyinjava", True)
    print(res)
    res=await spider.fetch("pyinjava", False)
    print(res)
    await spider.close()
    


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
