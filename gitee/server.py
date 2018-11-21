import asyncio
import json
import struct

from base.transport import Transport
from base.basetask import BaseTask
from gitee.taskprovider import TaskProvider
from logger import get_logger
from protocol import Protocol

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Server(Transport):
    
    def __init__(self, host="0.0.0.0", port=8792, task_pool=TaskProvider()):
        super().__init__()
        self._task_pool = task_pool
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
        if not self._task_pool.get_status():
            await self._task_pool.start()
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
            
            data = await self.get_data()
            logger.debug(f"get data:{data}")
            obj = json.loads(data.decode())
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
        data=json.dumps({"command": "start worker"}).encode()
        await self.request(header,data)
        res = await fut
        return res
    
    async def update_task(self, idx, data):
        logger.info("update_task"
                    f"repos num={len(data[1])}"
                    f"users num={len(data[2])}"
                    )
        for i in data[0]:
            t=BaseTask(i['name'],is_more=i["is_more"])
            await self._task_pool.complete(t)
        for i in data[3]:
            t=BaseTask(i['name'],is_more=i['is_more'])
            await self._task_pool.fail(t)
        for i in data[4]:
            t=BaseTask(i['name'])
            await self._task_pool.put(t)
        repos_task = []
        need_users_task = False
        for i in range(
                self._task_pool._max_buf - len(data[1])):
            task = await self._task_pool.get()
            if task:
                repos_task.append(task)
            else:
                need_users_task = True
                logger.warning("repos task not enough")
                break
        
        user_task = []
        if need_users_task:
            for i in range(
                    self._task_pool._max_buf - len(data[2])):
                task = await self._task_pool.get(more=True)
                if task:
                    user_task.append(task)
                else:
                    logger.warning(f"maybe no task")
        header = self.gen_header(fr=Protocol.Response, idx=idx)
        d = json.dumps({"repos": repos_task, "user": user_task})
        await self.request(header,d.encode())
    
    
    async def call_back(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        self._read = reader
        self._writer = writer
        self._connected = True
        self._conn_evt.set()
        logger.info(f"connected")


async def start(args=[("localhost",8889)]):
    task_pool=TaskProvider()
    logger.info("start muti servers")
    await task_pool.start()
    for i in args:
        srv = Server(host=i[0],port=i[1],task_pool=task_pool)
        logger.info(f"start server:{i[0]}:{i[1]}")
        await srv.start()
        f = await srv.start_worker()
    
    forever=asyncio.Future()
    await forever
    
def run(host="localhost",port=8888):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(host=host,port=port))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
