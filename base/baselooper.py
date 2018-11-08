#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio


__all__ = ["BaseLooper"]


class BaseLooper(object):
    def __init__(self):
        self._running = True
    
    async def start(self):
        """start server"""
        self._running = True
        print(type(self),"start")
    
    async def stop(self):
        """stop server"""
        self._running = False
        print(type(self),"stop")
    
    async def run(self):
        """
        execution task cycle
        """
        print(type(self),"run")
