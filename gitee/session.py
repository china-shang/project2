import os
import sys

from aiohttp import ClientSession
from statist import Statist

sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../"))
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../base"))

from logger import get_logger
logger=get_logger(__name__)

class Session(ClientSession):
    #Session with statistics
    statist = Statist()
    
    def __init__(self,statist=None, *args, **xargs):
        super().__init__(*args, **xargs)
        if statist:
            self.statist=statist
    async def _request(self, *args, **kargs):
        self.statist.increase_req()
        # logger.info("request")
        return await super()._request(*args, **kargs)
    
