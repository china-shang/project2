import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from gitee.taskprovider import *
from gitee.client import Client
from base.protocol import Protocol as Pro
from gitee.task import Task


class BaseTaskProviderProxy(TaskProvider):
    pass


class BaseTaskProviderProxy(TaskProvider):
    def __init__(self, client=Client(),name="test"):
        super().__init__()
        self._clt = client
        self.name=name
        update_evt=Event(EventType.UPDATE)
        self._get_repo_evt = update_evt
        self._get_user_evt =update_evt
        self._put_evt =update_evt
        self._complete_evt =update_evt
        self._fail_evt = update_evt
        
        self._events={update_evt}
        self._call_back: Dict[EventType, Coroutine] = {
            EventType.UPDATE: self.update,
        }

    async def start(self):
        """
        call super().start,await clt.control(),reply control
        :return:
        """
        await super(BaseTaskProvider,self).start()
        asyncio.ensure_future(self.run())
        # await self._clt.start()
        # data = await self._clt.control()
        # await self._clt.reply(data['idx'],
        #                       Pro.Control,
        #                       Pro.Success,
        #                       json.dumps(None).encode())
    async def update(self):
        logger.info(f"in update from {self.name}")
        req_data = self.export_buf()
        res = await self._clt.update_task(req_data.encode())
        logger.info(f"req={req_data},res={res} from {self.name}")
        if res['status'] == Pro.Fail:
            logger.error(f"error ")
            # TODO handle error
            return
        
        res_data = res['data']
        logger.info(f"res_data={res_data}")
        self.import_buf(res_data)
        
        for i in self._events:
            i.clear()
    
    def import_buf(self, data: dict):
        for i in range(5 - len(self._bak)):
            self._bak.append(set())
        self._put_buf.difference_update(
            self._bak.pop()
        )
        self._fail_buf.difference_update(
            self._bak.pop()
        )
        # self._get_buf_user.difference_update(
        self._bak.pop()
        # )
        # self._get_buf_repos.difference_update(
        self._bak.pop()
        # )
        self._complete_buf.difference_update(
            self._bak.pop()
        )
        repos={i['name'] for i in data["repos"]}
        self._get_buf_repos.update(repos)
        user={i['name'] for i in data["user"]}
        self._get_buf_user.update(user)
        print(self._get_buf_user)
        
        logger.info(f"len repos buf={len(self._get_buf_repos)}"
                    f"len users buf={len(self._get_buf_user)}"
                    )
    
    def export_buf(self):
        self._bak.clear()
        self._bak.append(self._complete_buf.copy())
        self._bak.append(self._get_buf_repos.copy())
        self._bak.append(self._get_buf_user.copy())
        self._bak.append(self._fail_buf.copy())
        self._bak.append(self._put_buf.copy())
        
        data = [list(i) for i in self._bak]
        
        res = json.dumps(data)
        return res


async def test():
    tp = BaseTaskProviderProxy()
    await tp.start()
    tp._clt: Client
    await tp._clt.start()
    data = await tp._clt.control()
    await tp._clt.reply(data['idx'],
                        Pro.Control,
                        Pro.Success,
                        json.dumps(None).encode())
    u = await tp.get()
    print(f"success get {u}")
    await asyncio.sleep(1000)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
