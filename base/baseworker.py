#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from .baselooper import BaseLooper


class BaseWorker(BaseLooper):
    def __init__(self, taskspool, store, statist):
        super().__init__()
        self._running = True
        self._task_pool = taskspool
        self._store = store
        self._statist = statist
    
    async def start(self):
        """
        start worker
        """
        await super().start()
        await self._task_pool.start()
        asyncio.ensure_future(self.run())
    
    async def stop(self):
        """
        stop worker
        """
        await super().stop()
        self._running = False
    
    async def pause(self):
        """
        pause worker
        """
        self._running = False
    
    async def restart(self):
        """
        restart worker
        """
        self._running = True
    
    async def run(self):
        """
        execution task cycle
        """
        await super().run()
    
    async def get_task(self):
        pass
    
    async def handle(self):
        pass
    
    async def _handle(self):
        pass
    
    async def _handle_more(self):
        pass
