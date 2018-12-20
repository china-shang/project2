#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0,os.path.realpath("../"))

import asyncio
import json
import struct

from base.basetask import BaseTask
from base.transport import Transport
from github.task import Task
from github.taskprovider import TaskProvider
from logger import get_logger
from config import Config
from protocol import Protocol

logger = get_logger(__name__)


# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][\n]
# [header:1+4+2+1=8

class Server(Transport):
    
    def __init__(self, host="0.0.0.0", port=8788, task_pool=TaskProvider()):
        super().__init__()
        self._task_pool = task_pool
        self._host = host
        self._port = port
        self._read: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
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
        if not self._task_pool.is_running():
            await self._task_pool.start()
        print(f"start server at {self._host}:{self._port}")
        asyncio.ensure_future(self.run())
        
        return
    
    async def stop(self):
        return await super().stop()
    
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
                
    async def run(self):
        while self._running:
            # if not self._connected:
            #     await self._conn_evt.wait()
            raw = await self._read.readexactly(10)
            # [from:1][index:4][which:2][status:1][data:?][eof]
            fr, idx, which, status = struct.unpack("!BLI?", raw)
            
            data=await self.get_data()
            
            logger.info(f"get data:{data}")
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
    
    # async def start_worker(self):
    #     idx = self.gen_idx()
    #     fut = asyncio.Future()
    #     self._fut_map[idx] = fut
    #
    #     header = self.gen_header(idx=idx, which=Protocol.Control)
    #     self._writer.write(header)
    #     json.dumps({"command": "start worker"}).encode()
    #     self._writer.write(b"\n")
    #     await self._writer.drain()
    #     await self.request(header,)
    #     res = await fut
    #     return res
    
    async def update_task(self, idx, data):
        logger.info("update_task")
        for i in data[0]:
            t=BaseTask(name=i['name'],is_more=i['is_more'])
            await self._task_pool.complete(t)
        for i in data[3]:
            t=BaseTask(name=i['name'],is_more=i['is_more'])
            await self._task_pool.fail(t)
        for i in data[4]:
            t=Task(name=i['name'], is_org=i["is_org"])
            await self._task_pool.put(t)
        repos_task = []
        need_users_task = False
        for i in range(
                self._task_pool._max_buf - len(data[1])):
            # get repos tasks
            task = await self._task_pool.get()
            if task:
                # has repos tasks
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
        data = json.dumps({"repos": repos_task, "user": user_task})
        logger.info(f"reply update")
        await self.request(header, data.encode())
    
    async def call_back(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        self._read = reader
        self._writer = writer
        self._connected = True
        self._conn_evt.set()
        logger.info(f"connected")


async def start(args=[("localhost",8888)]):
    task_pool=TaskProvider()
    logger.info("start muti servers")
    print(args)
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
    # loop.run_until_complete(start(args=[("localhost",8888),("54.250.173.187",1111)]))
    nodes=Config.nodesconfig['github']
    print(nodes)
    loop.run_until_complete(start(args=nodes))
    #loop.run_until_complete(start(args=[("localhost",8888)]))
    
if __name__ == '__main__':
    run()

