#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio

from aiohttp import web


# noinspection PyArgumentList
class A(object):
    def __hash__(self):
        return 1
    
    def __eq__(self, other):
        return 1
    
    async def test(self):
        app = web.Application()
        site = web.TCPSite()
        await site.start()
        loop = asyncio.get_event_loop()
        srv = await  loop.create_server()


s = {A(), A()}
print(len(s))
import sys
print(sys.path)
