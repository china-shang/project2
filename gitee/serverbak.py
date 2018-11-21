import asyncio
import json
import random
import struct
from gitee.task import Task
from gitee.taskprovider import *


from baselooper import BaseLooper
from logger import get_logger
from base.protocol import Protocol as Pro

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Server(BaseLooper):
    
    def __init__(self, host="0.0.0.0", port=8788,
                 taskprovider=TaskProvider()):
        super().__init__()
        self._task_pool=taskprovider
        self._host = host
        self._port = port
        self._read: asyncio.StreamReader
        self._writer: asyncio.StreamWriter
        self._connected = False
        self._conn_evt = asyncio.Event()
        self._conn_evt.clear()
        self._idx_set = set()
    
    async def start(self):
        self._read, self._writer = await asyncio.open_connection(
            self._host, self._port)
        asyncio.ensure_future(self.run())
        
        return await super().start()
    
    async def stop(self):
        return await super().stop()
    
    async def run(self):
        while self._running:
            if not self._connected:
                await self._conn_evt.wait()
            raw = await self._read.readexactly(8)
            # [from:1][index:4][which:2][status:1][data:?][eof]
            fr, idx, which, status = struct.unpack("!BLI?", raw)
            
            data = self._read.read()
            obj = json.loads(data)
            await self.handle(fr, idx, which, status, obj)
    
    async def handle(self, fr, idx, which, status, obj):
        if fr == Pro.Request:
            await self._handle_req(idx, which, obj)
        else:
            await self._handle_res(idx, which, status, obj)
    
    async def _handle_req(self, idx, which, obj: dict):
        if which==Pro.TaskDispatch:
            await self.req_update_task(idx,obj)
            
    
    async def start_worker(self):
        idx=self.gen_idx()
        data=struct.pack("!BLI?",Pro.Request,
                    idx,Pro.Control,Pro.Success)
        print(len(data))
        
        self._writer.write(data)
        self._writer.write(json.dumps({"command":"start worker"}).encode())
        self._writer.write(b"\n")
        await self._writer.drain()
        await self._read.read()
    
    async def _handle_res(self, idx, which, status, obj):
        self._idx_set.remove(idx)
        if status == Pro.Fail:
            logger.error(f"error={obj}")
            return
    
    async def req_update_task(self,obj:dict):
        pass
    
    async def call_back(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        self._read = reader
        self._writer = writer
        self._connected = True
        self._conn_evt.set()
    
    def gen_idx(self) -> int:
        idx = random.randint(0, 0xff_ff_ff_ff)
        while idx in self._idx_set:
            idx = random.randint(0, 0xff_ff_ff_ff)
        self._idx_set.add(idx)
        return idx
    
async def test():
    srv=Server()
    await srv.start()
    await srv.start_worker()

if __name__=="__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
