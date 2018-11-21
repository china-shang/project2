import asyncio
import json
import struct

from .transport import Transport
from logger import get_logger
from protocol import Protocol

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Server(Transport):
    
    def __init__(self, host="0.0.0.0", port=8788):
        super().__init__()
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
        self._connected = True
        self._conn_evt.set()
        await super().start()
        print(f"start server at {self._host}:{self._port}")
        asyncio.ensure_future(self.run())
        
        return
    
    async def stop(self):
        return await super().stop()
    
    async def run(self):
        while self._running:
            # if not self._connected:
            #     await self._conn_evt.wait()
            raw = await self._read.readexactly(10)
            # [from:1][index:4][which:2][status:1][data:?][eof]
            fr, idx, which, status = struct.unpack("!BLI?", raw)
            
            data = await self._read.readline()
            logger.info(f"get data:{data}")
            obj = json.loads(data[:-1])
            await self.handle(fr, idx, which, status, obj)
    
    async def handle(self, fr, idx, which, status, obj):
        if fr == Protocol.Request:
            logger.info(f"handle req {idx}")
            await self._handle_req(idx, which, obj)
        else:
            logger.info(f"handle res {idx}")
            await self._handle_res(idx, which, status, obj)
    
    async def _handle_req(self, idx, which, obj: dict):
        if which == Protocol.TaskDispatch:
            await self.update_task(idx, obj)
    
    async def _handle_res(self, idx, which, status, obj):
        self._idx_set.remove(idx)
        if which == Protocol.TaskDispatch:
            fut = self._fut_map.pop(idx)
            fut.set_result({"status": status, "data": obj})
        if which == Protocol.Control:
            fut = self._fut_map.pop(idx)
            fut.set_result({"status": status, "data": obj})
        # fut = self._fut_map.pop(idx)
        # fut.set_result({"status":status,"data":obj})

    async def start_worker(self):
        idx = self.gen_idx()
        fut = asyncio.Future()
        self._fut_map[idx] = fut
    
        header = self.gen_header(idx=idx, which=Protocol.Control)
        self._writer.write(header)
        self._writer.write(json.dumps({"command": "start worker"}).encode())
        self._writer.write(b"\n")
        await self._writer.drain()
        
        res = await fut
        return res

    async def update_task(self):
        pass
    
    async def reply(self, idx, which, status, data):
        header = self.gen_header(fr=Protocol.Response,
                                 idx=idx, which=which, status=status)
        self._writer.write(header)
        self._writer.write(data)
        self._writer.write("\n")
        await self._writer.drain()
    
    async def call_back(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        self._read = reader
        self._writer = writer
        self._connected = True
        self._conn_evt.set()
        logger.info(f"connected")


async def test():
    srv = Server()
    await srv.start()
    f = await srv.start_worker()
    print(f"f={f}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
