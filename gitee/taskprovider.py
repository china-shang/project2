#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import *
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from gitee.mysqlclient import MysqlClient
from base.basetaskprovider import BaseTaskProvider
from gitee.task import Task
from base.basetaskprovider import *


class TaskProvider(BaseTaskProvider):
    """
    communicate with datasource and provide api for upper layer service
    """
    
    def __init__(self,client=MysqlClient()):
        super().__init__(client=client)

        self._call_back: Dict[EventType, Coroutine] = {
            EventType.GETREPO: self._get_repo,
            EventType.GETUSER: self._get_user,
            EventType.PUT: self._put,
            EventType.COMPLETE: self._complete,
            EventType.FAIL: self._fail
        }
    
    async def start(self):
        await super().start()
        await self._client.connection()
        asyncio.ensure_future(self.run())
    
    async def stop(self):
        await super().stop()
        await self._client.close()

    async def _get_repo(self):
        repos=await self._client.get()
        self._get_buf_repos.update(repos)
    
    async def _get_user(self):
        users=await self._client.get(users=True)
        print(users)
        self._get_buf_user.update(users)

    async def _put(self):
        await self._client.put({i['name'] for i in self._put_buf})

    async def _complete(self):
        s={(i.name,i.is_more) for i in self._complete_buf}
        await self._client.complete(s)

    async def _fail(self):
        s={(i.name,i.is_more) for i in self._fail_buf}
        await self._client.fail(s)
    
    
async def test():
    tp=TaskProvider()
    await tp.start()
    await tp.put(Task("jsddff"))
    u=await tp.get()

if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()

