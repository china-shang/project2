#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
realpath=os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0,realpath)

import asyncio
import json

from base.baseworkerpool import BaseWorkerPool
from logger import get_logger
from gitee.taskproviderproxy import BaseTaskProviderProxy
from gitee.worker import Worker
from gitee.client import Client
from statist import Statist
from datastore import Store
from base.protocol import Protocol as Pro
from config import Config
from pympler import muppy,summary,tracker
import objgraph
import gc

logger = get_logger(__name__)


class WorkerPool(BaseWorkerPool):
    def __init__(self, statist: Statist = Statist(), max_size=4,host="localhost",port=8888):
        super().__init__(statist, max_size)
        self._clt=Client(host=host,port=port)
        self._task_pool=BaseTaskProviderProxy(client=self._clt,name="nobug")
        self.store=Store()
        self.statist=Statist()
        self._workers_pending=set()
        self._workers_running=set()
        self.done=asyncio.Future()
        
        self.test=True
        
        for i in range(max_size):
            w=Worker(self._task_pool,self.store,statist,name=f"worker{i}")
            self._workers_pending.add(w)
    
    def increase_worker(self, count=1):
        if self.now+count>self._max_size:
            logger.info(f"worker num will > max_size")
            return
        for i in range(count):
            w=self._workers_pending.pop()
            self._workers_running.add(w)
            asyncio.ensure_future(w.start())
        super().increase_worker(count)
    
    def decrease_worker(self, count=1):
        if self.now-count<1:
            logger.info(f"worker num will < 1")
            return
        for i in range(count):
            w=self._workers_running.pop()
            self._workers_pending.add(w)
            asyncio.ensure_future(w.stop())
        super().decrease_worker(count)
    
    async def run(self):
        while self._running:
            repos_rate_req_rate, users_rate, req_rate = \
                self._statist.get_recent_speed()
            
            # if req_rate > RateLimit.get_req_rate_limit() * 1.2:
            #     self.decrease_worker()
            #
            # if req_rate < RateLimit.get_req_rate_limit() * 0.8:
            #     self.increase_worker()
            logger.info(f"recent_repos_rate={repos_rate_req_rate:.2f} "
                        f"recent_users_rate={users_rate:.2f}")
            logger.info(f"all get repos{self.statist.all_repo} "
                        f"all complete users{self.statist.all_user}"
                        )
            
            await asyncio.sleep(5)
            
            if self.test:
                self.test=False
                objs=muppy.get_objects()
                sum1=summary.summarize(objs)
                ls=muppy.filter(objs,type([]))
                import random
                import time
                idx=random.randint(0,len(ls))
                file_name=str(time.time())+".png"
                objgraph.show_refs(ls[idx:idx+3],filename=file_name)
                objgraph.show_refs()
                print(f"objs count ={gc.get_count()}")
                
    
    async def start(self):
        await super().start()
        await self._clt.start()
        data = await self._clt.control()
        await self._clt.reply(data['idx'],
                              Pro.Control,
                              Pro.Success,
                              json.dumps(None).encode())
        for i in self._workers_pending:
            await i.start()
            self._workers_running.add(i)
        self._workers_pending.clear()
        asyncio.ensure_future(self.run())
    
    async def stop(self):
        return await super().stop()

async def test(host="localhost",port=8888):
    pool=WorkerPool(host=host,port=port)
    await pool.start()
    await pool.done
    
def run(host="localhost",port=8888):
    loop=asyncio.get_event_loop()
    config=Config.nodeconfig['gitee']
    loop.run_until_complete(test(**config))
    

if __name__ == '__main__':
    run()
    

