#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TODO if remaining task for repos is too little, change task to users task auto

import asyncio
from enum import Enum
from typing import *

from logger import get_logger
from .baselooper import BaseLooper
from .basemysqlclient import BaseMysqlClient
from .basetask import BaseTask

logger = get_logger(__name__)


class EventType(Enum):
    GETREPO = 1
    GETUSER = 2
    PUT = 3
    COMPLETE = 4
    FAIL = 5
    UPDATE=6


class Event(asyncio.Event):
    def __init__(self, t: EventType):
        super().__init__()
        self.type = t
    
    async def wait(self):
        await super().wait()
        return self
    
    def __hash__(self):
        return hash(self.type)
    
    def __eq__(self, other):
        if isinstance(other, Event):
            return self.type == other.type
        return False


class BaseTaskProvider(BaseLooper):
    """
    communicate with datasource and provide api for upper layer service
    """
    
    def __init__(self, client=BaseMysqlClient()):
        super().__init__()
        self._bak = []
        self._client = client
        self._get_repo_evt = Event(EventType.GETREPO)
        self._get_user_evt = Event(EventType.GETUSER)
        self._put_evt = Event(EventType.PUT)
        self._complete_evt = Event(EventType.COMPLETE)
        self._fail_evt = Event(EventType.FAIL)
        self._max_buf = 30
        self._done = asyncio.Event()
        self._events:Set[asyncio.Event] = {self._get_repo_evt, self._get_user_evt,
                        self._put_evt, self._complete_evt,
                        self._fail_evt
                        }
        
        self._call_back: Dict[EventType, Coroutine] = {
            EventType.GETUSER: self._get_repo,
            EventType.GETREPO: self._get_user,
            EventType.PUT: self._put,
            EventType.COMPLETE: self._complete,
            EventType.FAIL: self._fail
        }
        
        self._get_buf_repos: Set[BaseTask] = set()
        self._get_buf_user: Set[BaseTask] = set()
        self._complete_buf: Set[BaseTask] = set()
        self._fail_buf: Set[BaseTask] = set()
        self._put_buf: Set[BaseTask] = set()
    
    async def start(self):
        await super().start()
        await self._client.connection()
    
    async def stop(self):
        await super().stop()
        await self._client.close()
    
    async def run(self):
        while True:
            self._done.set()
            events: List[Event] = await self.wait_event()
            for e in events:
                if not e.is_set():
                    continue
                e.clear()
                callback = self._call_back[e.type]
                await callback()
                e.clear()
                # event has handle
    
    async def wait_event(self):
        done, pending = await asyncio.wait(
            [i.wait() for i in self._events],
            return_when="FIRST_COMPLETED")
        for i in pending:
            i: asyncio.Future
            i.cancel()
            # cancel pending task
        evts = {i.result() for i in done}
        return evts
    
    def _get_task(self, more=False):
        if more:
            name = self._get_buf_user.pop()
            res = BaseTask(name=name, is_more=more)
        else:
            name = self._get_buf_repos.pop()
            res = BaseTask(name=name, is_more=more)
        
        return res
    
    async def get(self, more=False) -> set:
        """
        if more = true get tasks that use for getting more users,
        otherwise get tasks that use for fetching data
        """
        res = None
        retry_count = 5
        if more:
            if len(self._get_buf_user) > 0:
                res = self._get_task(more)
            else:
                while retry_count and len(self._get_buf_user) < 1:
                    retry_count -= 1
                    # if no buf ,get data
                    self._get_user_evt.set()
                    self._done.clear()
                    await self._done.wait()
                    if len(self._get_buf_user) > 0:
                        logger.info(f"no repos,now get user task")
                        res = self._get_task(more)
                        break
        else:
            if len(self._get_buf_repos) > 0:
                res = self._get_task(more)
            else:
                while retry_count and len(self._get_buf_repos) < 1:
                    retry_count -= 1
                    # if no buf ,get data
                    self._get_repo_evt.set()
                    self._done.clear()
                    await self._done.wait()
                    if len(self._get_buf_repos) > 0:
                        res = self._get_task(more)
                        break
            # name = self._get_buf_repos.pop()
        if not retry_count:
            await self.refresh()
            await asyncio.sleep(3)
            # return await self.get(more=more)
            logger.warning("can not get task")
            return None
        return res
    
    async def put(self, task: BaseTask):
        """
        put  task
        """
        self._put_buf.add(task)
        # logger.debug(f"will put task{task.name}")
        if len(self._put_buf) > self._max_buf:
            self._put_evt.set()
    
    async def complete(self, task):
        """
        mark task complete
        """
        self._complete_buf.add(task)
        # logger.debug(f"will complete task{task.name}")
        if len(self._complete_buf) > self._max_buf:
            self._complete_evt.set()
    
    async def fail(self, task: set):
        """
        mark tasks fail
        
        :param task:tasks will  marked fail
        """
        self._fail_buf.add(task)
        logger.debug(f"will fail task{task.name}")
        self._fail_evt.set()
        # TODO wait buf full
    
    async def refresh(self):
        """
        refresh put buf and complete buf
        :return:
        """
        logger.info(f"will refresh")
        self._put_evt.set()
        self._complete_evt.set()
    
    async def _get_repo(self) -> set:
        """
        if more = true get tasks that use for getting more users,
        otherwise get tasks that use for fetching data
        """
        pass
    
    async def _get_user(self) -> set:
        print("bug")
        """
        if more = true get tasks that use for getting more users,
        otherwise get tasks that use for fetching data
        """
        pass
    
    async def _put(self):
        print("bug")
        """
        put  tasks
        """
        pass
    
    async def _complete(self):
        print("bug")
        """
        mark tasks complete
        """
        pass
    
    async def _fail(self):
        """
        mark tasks fail
        
        :param task:tasks will  marked fail
        """
        pass
    
    def import_buf(self, data: dict):
        self._put_buf.difference_update(
            self._bak.pop()
        )
        self._fail_buf.difference_update(
            self._bak.pop()
        )
        # self._get_buf_user.difference_update(
        #     self._bak.pop()
        # )
        # self._get_buf_repos.difference_update(
        #     self._bak.pop()
        # )
        self._complete_buf.difference_update(
            self._bak.pop()
        )
        {BaseTask(i['name'],i['is_more'])}
        self._get_buf_repos.update(set(data["repos"]))
        self._get_buf_user.update(set(data["user"]))
    
    def export_buf(self):
        self._bak.append(self._complete_buf.copy())
        self._bak.append(self._get_buf_repos.copy())
        self._bak.append(self._get_buf_user.copy())
        self._bak.append(self._fail_buf.copy())
        self._bak.append(self._put_buf.copy())
        
        data=[list(i) for i in self._bak]
        return data
        
        
