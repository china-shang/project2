import asyncio
import json
import struct

from base.transport import Transport
from logger import get_logger
from base.protocol import Protocol
import gc

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Client(Transport):
    
    def __init__(self, host="0.0.0.0", port=8792):
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
        self._srv = await asyncio.start_server(self.call_back,
                                               host=self._host,
                                               port=self._port)
        print(f"start client at {self._host}:{self._port}")
        await super().start()
        asyncio.ensure_future(self.run())
        
        return
    
    async def stop(self):
        return await super().stop()
    
    async def run(self):
        while self._running:
            if not self._connected:
                await self._conn_evt.wait()
            logger.info("listening")
            raw = await self._read.read(10)
            if self._read.at_eof() or len(raw)==0:
                logger.warning("at eof,now sleep 3s")
                await asyncio.sleep(3)
            else:
                # print(raw)
                # [from:1][index:4][which:2][status:1][data:?][eof]
                fr, idx, which, status = struct.unpack("!BLI?", raw)
                
                data = await self.get_data()
                obj = json.loads(data.decode())
                print(obj)
                await self.handle(fr, idx, which, status, obj)
    
    async def handle(self, fr, idx, which, status, obj):
        if fr == Protocol.Request:
            logger.info(f"handle req {idx}")
            await self._handle_req(idx, which, obj)
        else:
            logger.info(f"handle res {idx}")
            await self._handle_res(idx, which, status, obj)
            # self._idx_set.remove(idx)
    
    async def _handle_req(self, idx, which, obj:dict):
        if which==Protocol.Control:
            logger.info(f"get control req {idx} data:{obj}")
            self._control_fut.set_result({"idx":idx,"data":obj})

    async def control(self):
        """
        receive server control
        :return:
        """
        res=await self._control_fut
        self._control_fut=asyncio.Future()
        return res

    async def reply(self, idx,which,status,data):
        header=self.gen_header(fr=Protocol.Response,
                               idx=idx,which=which,status=status)
        await self.request(header,data)
        logger.info(f"will reply {idx}")
        
    async def _handle_res(self, idx, which, status, obj):
        self._idx_set.remove(idx)
        if which==Protocol.TaskDispatch:
            fut=self._fut_map.pop(idx)
            fut.set_result({"status":status,"data":obj})

    async def update_task(self, data=None):
        idx=self.gen_idx()
        fut=asyncio.Future()
        self._fut_map[idx]=fut

        header=self.gen_header(idx=idx)
        await self.request(header,data)
        res=await fut
        return res
        

    async def call_back(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        self._read = reader
        self._writer = writer
        self._connected = True
        self._conn_evt.set()
        logger.info(f"connected")
    
    
async def test():
    srv=Client()
    await srv.start()
    data=await srv.control()
    await srv.reply(data['idx'],
                    Protocol.Control,
                    Protocol.Success,
                    json.dumps(None).encode())
    print(f"data={data}")
    
    srv.update_task()
    await asyncio.sleep(1000)

if __name__=="__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
