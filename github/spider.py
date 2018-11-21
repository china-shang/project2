import asyncio
import os
import sys
import time

import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.basespider import BaseSpider
from github.session import Session
from config import Config

from logger import get_logger

logger = get_logger(__name__)


class Spider(BaseSpider):
    header = {
        "Authorization": f"bearer  {Config.githubtoken['key']}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }
    api_url = "https://api.github.com/graphql"
    
    def __init__(self, timeout=aiohttp.ClientTimeout(total=60)):
        self._timeout = timeout
        self._session = Session(headers=self.header,
                                timeout=self._timeout)
    
    async def fetch(self, data):
        await super().fetch("")
        if not self._session or self._session.closed:
            self._session = Session(headers=self.header,
                                    timeout=self._timeout)
        async with self._session.post(self.api_url, json=data) as resp:
            remaining = resp.headers.get('X-RateLimit-Remaining')
            reset_time = float(resp.headers.get('X-RateLimit-Reset'))
            logger.info(f"remain={remaining},reset={time.ctime(reset_time)}")
            if remaining == 0:
                logger.warning(f"no remain req count ,sleep 30s")
                await asyncio.sleep(30)
            res = await resp.json()
            return res
    
    def close(self):
        self._session.close()
    
    def closed(self):
        return self._session.closed
