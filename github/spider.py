import os
import sys

import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.basespider import BaseSpider
from github.session import Session


class Spider(BaseSpider):
    header = {
        "Authorization": f"bearer  {key['key']}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }
    api_url = "https://api.github.com/graphql"
    
    def __init__(self,timeout=aiohttp.ClientTimeout(60)):
        self._timeout=timeout
        self._session = Session(headers=self.header,
                                timeout=aiohttp.ClientTimeout(self._timeout))
    
    async def fetch(self, data):
        await super().fetch("")
        if not self._session or self._session.closed:
            self._session=Session(headers=self.header,
                                  timeout=self._timeout)
        async with self._session.post(self.api_url, json=data) as resp:
            res = await resp.json()
            return res
    
    def close(self):
        self._session.close()
    
    def closed(self):
        return self._session.closed
