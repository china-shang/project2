import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../"))
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../base"))
import asyncio


from base.basetask import BaseTask

class Task(BaseTask):
    # delagation = BaseTask.delagation.update({"is_recommend"})
    pass

async def test():
    #BUG
    Task("df")

if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()


