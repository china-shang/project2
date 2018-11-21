import asyncio
import os
import sys
import time

from aiohttp import ClientSession

sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../"))
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../base"))

from logger import get_logger
logger=get_logger(__name__)
from statist import Statist

class Session(ClientSession):
    #Session with statistics
    statist = Statist()
    
    def __init__(self,statist=None, *args, **xargs):
        super().__init__(*args, **xargs)
        if statist:
            self.statist=statist
    
    async def _request(self, *args, **kargs):
        self.statist.increase_req()
        logger.debug(f"{self.statist.get_avg_speed()[2]:.2f}")
        _, _, rate = self.statist.get_avg_speed()
        if rate > 1.0:
            expect_time = self.statist.req_count / 1.0
            during = time.time() - self.statist.start_time
            sleep_time = (expect_time - during) * 1.1
            logger.warning(f"overspeed , then sleep {sleep_time}")
            await asyncio.sleep(sleep_time)
        return await super()._request(*args, **kargs)
    
