import json
import os
import time

from logger import get_logger

logger = get_logger(__name__)


class Store(object):
    def __init__(self, dir="data", prefix="repos"):
        self._buf = []
        self._max_buf_count = 1000
        # if  than this,will store
        self._dir = dir
        self._prefix = prefix
        self.path = self.new_file()
        self._now = 0
    
    async def put(self, data: list):
        if len(data) == 0:
            logger.info(f"no data put to store")
            return
        
        logger.info(f"put {len(data)} to store")
        self._buf.extend(data)
        self._now += len(data)
        if self._now > self._max_buf_count:
            self._now = 0
            self.path = self.new_file()
        self.store()
    
    def new_file(self) -> str:
        file_name = self._prefix + str(round(time.time() * 1000))
        logger.info(f"will store {len(self._buf)} to {file_name}")
        if os.path.isdir(self._dir):
            # join path
            path = os.path.join(self._dir, file_name)
        else:
            # path does not exist , store the current dir
            path = os.path.join(file_name)
        return path
    
    def store(self):
        with open(self.path, "a") as fp:
            json.dump(self._buf, fp)
        
        self._buf.clear()
        # clear buffer
