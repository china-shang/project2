from multiprocessing import Pool
from gitee.workerpool import *
import time
import gitee.server
import asyncio
import asyncio



def start(count=4):
    pool=Pool(count)
    args=[
        ("localhost",8888),
        ("localhost",8889),
        ("localhost",8890),
        ("localhost",8891)
    ]
    pool.starmap_async(run,args)
    time.sleep(6)
    logger.info("will start server")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gitee.server.start(args))
    
def test(a,b):
    print(f"{a}&{b}")
    
    
async def work(host="localhost",port=8888):
    worker_pool=WorkerPool()
    await worker_pool.start()
    await worker_pool._fut
    
if __name__ == '__main__':
    start()
    
    
    






