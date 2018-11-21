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
        if 3:
            a=3
        else:
            a=4
        async def t1():
            if a:
                a=3
        await t1()
    


s = {A(), A()}
print(len(s))
import sys
asyncio.get_event_loop().run_until_complete(A().test())
print(sys.path)
