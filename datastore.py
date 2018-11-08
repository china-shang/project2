import json
import os
import time


class Store(object):
    def __init__(self, dir="data", prefix="repos"):
        self._buf = set()
        self._max_buf_count = 100
        # if  than this,will store
        self._dir = dir
        self._prefix = prefix
    
    async def put(self, data: set):
        self._buf.update(data)
        if len(self._buf) >= self._max_buf_count:
            self.store()
    
    def store(self):
        file_name = self._prefix + str(round(time.time() * 1000))
        if os.path.isdir(self._dir):
            # join path
            path = os.path.join(self._dir, file_name)
        else:
            # path does not exist , store the current dir
            path = os.path.join(file_name)
        with open(path, "a") as fp:
            json.dump(list(self._buf), fp)
            
        self._buf.clear()
        # clear buffer
