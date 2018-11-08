#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .baselooper import BaseLooper
class WorkerPool(BaseLooper):
    """
    worker pool 
    """
    async def increase_worker(self, count=1):
        pass

    async def decrease_worker(self, count=1):
        pass



