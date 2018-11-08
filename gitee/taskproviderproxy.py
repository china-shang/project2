import sys,os
import asyncio
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../"))
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../base"))

from base.basetaskprovider import BaseTaskProvider
from gitee.taskprovider import TaskProvider
from gitee.task import Task

class BaseTaskProviderProxy(TaskProvider):
    pass

async def test():
    tp=BaseTaskProviderProxy()
    await tp.start()
    u=await tp.get()
    print(u)

if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()

