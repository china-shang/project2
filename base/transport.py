import asyncio
import json
import random
import struct
from typing import *

from .baselooper import BaseLooper
from logger import get_logger
from .protocol import Protocol

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Transport(BaseLooper):
    
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
        self._control_fut=asyncio.Future()
        self._fut_map:Dict[int,asyncio.Future]={}

    async def get_data(self):
        find=False
        data=b""
        while not find:
            try:
                t=await self._read.readuntil(b"\n")
                find=True
                data+=t
            except asyncio.LimitOverrunError as e:
                t=await self._read.read(e.consumed+1)
                if "is found" in e.args[0]:
                    find=True
                data+=t
        data=data[:-1]
    
        return data
    
    async def start(self):
        # self._srv = await asyncio.start_server(self.call_back,
        #                                        host=self._host,
        #                                        port=self._port)
        # print(f"start server at {self._host}:{self._port}")
        # asyncio.ensure_future(self.run())
        
        return await super().start()
    
    async def stop(self):
        return await super().stop()
    
    async def update_task(self,idx,data):
        
        pass
    
    async def control(self):
        pass

    async def start_worker(self):
        idx = self.gen_idx()
        fut = asyncio.Future()
        self._fut_map[idx] = fut
    
        header = self.gen_header(idx=idx, which=Protocol.Control)
        data=json.dumps({"command": "start worker"}).encode()
        await self.request(header,data)
        res = await fut
        return res
    
    async def reply(self, idx,which,status,data):
        """
        
        :param idx: index of request
        :param which: which operation
        :param status:status of request,e.g. Protocol.Success Protocol.Fail
        :param data:binary data of reply
        :return:
        """
        header = self.gen_header(fr=Protocol.Response,
                                 idx=idx, which=which, status=status)

        await self.request(header,data)
    
    async def request(self,header,data):
        """
        write data to socket
        :param header: Protocol binary header
        :param data: binary data
        :return:
        """
        self._read: asyncio.StreamReader
        self._writer: asyncio.StreamWriter
        self._writer.write(header)
        self._writer.write(data)
        self._writer.write(b"\n")
        return await self._writer.drain()
    
    def gen_idx(self) -> int:
        idx = random.randint(0, 0xff_ff_ff_ff)
        while idx in self._idx_set:
            idx = random.randint(0, 0xff_ff_ff_ff)
        self._idx_set.add(idx)
        return idx

    def gen_header(self,fr=Protocol.Request,idx=-1,
                   which=Protocol.TaskDispatch,
                   status=Protocol.Success):
        
        if idx==-1:
            idx=self.gen_idx()
            
        return struct.pack("!BLI?", fr,idx,which,status)
        
