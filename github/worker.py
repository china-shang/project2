import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.baseworker import BaseWorker
from github.taskhander import TaskHander
from github.chain import Chain
from github.spider import Spider
from github.taskproviderproxy import BaseTaskProviderProxy
from github.task import Task
from github.taskhander import TaskHander
from statist import Statist
from datastore import Store

from logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pass


# noinspection PyTypeChecker,PyBroadException
class TaskTypeError(Exception):
    pass


class Worker(BaseWorker):
    def __init__(self, taskspool: BaseTaskProviderProxy,
                 store: Store, statist: Statist,name=""):
        super().__init__(taskspool, store, statist,name=name)
        
        self._name=name
        self._spider = Spider()
        self._task: Task
        self._task_pool = taskspool
        self._statist=statist
        self._store=store
        self._hander=TaskHander(None,spider=self._spider)

    async def start(self):
        await super().start()
        await self._hander.start()

    async def run(self):
        while self._running:
            self._task = await self.get_task()
            if self._task:
                try:
                    await self.handle()
                    self._statist.increase_user()
                    await self._task_pool.complete(self._task)
                except Exception as e:
                    await self._task_pool.fail(self._task)
                    # raise e
                    #TODO handle exception
            else:
                await asyncio.sleep(3)
                # no task
    
    async def handle(self):
        repos,users,orgs=await self._hander.handle(self._task)
        
        self.extract_owners(users)
        self.extract_owners(orgs,is_org=True)
        self.extrack_repos(repos)
    
    async def get_task(self):
        task = await self._task_pool.get()
        if task:
            logger.info(f"get repos task {task.name}")
            return task
        else:
            task = await self._task_pool.get(more=True)
            if task:
                logger.info(f"get users task {task.name}")
                return task
            else:
                # maybe no task
                logger.info(f"no any task")
                return None
        return task
    
    # async def _handle(self):
    #     if not self._task:
    #         await asyncio.sleep(10)
    #     if self._task.is_org:
    #         await self._handle_org()
    #     else:
    #         is_usr = await self._handle_user()
    #         if not is_usr:
    #             await self._handle_org()
    #
    # # TODO get more attr like forked
    #
    # async def _handle_org(self):
    #     if self._task.is_more:
    #         has_more_members = True
    #         has_more_repos = False
    #         # only fetch users
    #     else:
    #         has_more_members = False
    #         has_more_repos = True
    #         # only fetch repos
    #
    #     # noinspection PyUnresolvedReferences
    #     def _gen_chain(init=False):
    #         if init:
    #             if self._task.is_more:
    #                 chain = Chain("organization") \
    #                     (login=self._task.name) \
    #                     .get(Chain("members") \
    #                              (first=100) \
    #                          .get(Chain("pageInfo") \
    #                               .get("endCursor hasNextPage")) \
    #                          .nodes \
    #                          .get("login"))
    #             else:
    #                 chain = Chain("organization") \
    #                     (login=self._task.name) \
    #                     .get(Chain("repositories") \
    #                              (first=100) \
    #                          .get(Chain("pageInfo") \
    #                               .get("endCursor hasNextPage")) \
    #                          .nodes \
    #                          .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
    #                          .get(Chain("languages")
    #                               (first=100) \
    #                               .nodes \
    #                               .get("name")) \
    #                          .get(Chain("parent")
    #                               .get("projectsUrl")) \
    #                          .get(Chain("licenseInfo")
    #                               .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
    #                          .get(Chain("stargazers") \
    #                                   (first=1) \
    #                               .get("totalCount")) \
    #                          .get(Chain("watchers") \
    #                                   (first=1) \
    #                               .get("totalCount")) \
    #                          )
    #             return chain
    #
    #         chain = Chain("organization") \
    #             (login=self._task.name)
    #
    #         if has_more_members:
    #             chain = chain.get(Chain("members") \
    #                                   (first=100,
    #                                    after=members_end_cursor) \
    #                               .get(Chain("pageInfo") \
    #                                    .get("endCursor hasNextPage")) \
    #                               .nodes \
    #                               .get("login"))
    #
    #         if has_more_repos:
    #             chain = chain \
    #                 .get(Chain("repositories") \
    #                          (first=100, after=repos_end_cursor) \
    #                      .get(Chain("pageInfo") \
    #                           .get("endCursor hasNextPage")) \
    #                      .nodes \
    #                      .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
    #                      .get(Chain("languages")
    #                           (first=100) \
    #                           .nodes \
    #                           .get("name")) \
    #                      .get(Chain("parent")
    #                           .get("projectsUrl")) \
    #                      .get(Chain("licenseInfo")
    #                           .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
    #                      .get(Chain("stargazers") \
    #                               (first=1) \
    #                           .get("totalCount")) \
    #                      .get(Chain("watchers") \
    #                               (first=1) \
    #                           .get("totalCount")) \
    #                      )
    #         return chain
    #
    #     async def _handle_result():
    #
    #         users = set()
    #         repos = []
    #         nonlocal has_more_members, has_more_repos
    #         if has_more_members:
    #             has_more_members = data['organization'] \
    #                 ['members']['pageInfo']['hasNextPage']
    #             members_end_cursor = data['organization'] \
    #                 ['members']['pageInfo']['endCursor']
    #             res = self.extract_owners(data['organization'] \
    #                                           ['members']['nodes'])
    #             users.update(res)
    #
    #         if has_more_repos:
    #             has_more_repos = data['organization'] \
    #                 ['repositories']['pageInfo']['hasNextPage']
    #             repos_end_cursor = data['organization'] \
    #                 ['repositories']['pageInfo']['endCursor']
    #             res = self.extrack_repos(data['organization'] \
    #                                          ['repositories']['nodes'])
    #             repos.extend(res)
    #
    #         if self._task.is_more:
    #             logger.info(f"get users {len(users)} from {self._task.name}")
    #         else:
    #             logger.info(f"get repos {len(repos)} from {self._task.name}")
    #
    #         for i in users:
    #             await self._task_pool.put(i)
    #         await self._store.put(repos)
    #         if not (has_more_members or has_more_repos):
    #             # no data
    #             return False
    #         return True
    #
    #     chain = _gen_chain(init=True)
    #     while self._running:
    #         try:
    #             raw_data = await self._spider.fetch(chain.to_dict())
    #             if raw_data['data'] is None:
    #                 logger.warn(f"data is None, result = {raw_data}")
    #                 if "error" in raw_data and raw_data['error'][0]['type']=='RATE_LIMITED':
    #                     self._statist.record_error()
    #                 return None
    #             if raw_data['data']['organization']:
    #                 logger.warning(f"{self._task.name} is org.")
    #                 return False
    #             data = raw_data['data']
    #         except KeyError:
    #             logger.error(f"result = {raw_data}")
    #             if "abuse" in raw_data['documentation_url']:
    #                 self.handle_abuse()
    #                 return None
    #         except Exception:
    #             logger.error(f"result = {raw_data}")
    #
    #         has_more = await _handle_result()
    #         if not has_more:
    #             # no more data
    #             break
    #
    # async def _handle_user(self):
    #     if self._task.is_more:
    #         # only fetch users
    #         has_more_followers = True
    #         has_more_following = True
    #         has_more_orgs = True
    #         has_more_repos = False
    #     else:
    #         # only fetch repos
    #         has_more_followers = False
    #         has_more_following = False
    #         has_more_orgs = False
    #         has_more_repos = True
    #     def _gen_chain(init=False):
    #         if init:
    #             if self._task.is_more:
    #                 # only get users
    #                 c = Chain("user") \
    #                     (login=self._task.name) \
    #                     .get(Chain("followers")
    #                          (first=100) \
    #                          .get(Chain("pageInfo")
    #                               .get("endCursor hasNextPage"))
    #                          .nodes
    #                          .get("login")) \
    #                     .get(Chain("following")
    #                          (first=100)
    #                          .get(Chain("pageInfo")
    #                               .get("endCursor hasNextPage"))
    #                          .nodes
    #                          .get("login")) \
    #                     .get(Chain("organizations")
    #                          (first=100)
    #                          .get(Chain("pageInfo")
    #                               .get("endCursor hasNextPage"))
    #                          .nodes
    #                          .get("login"))
    #             else:
    #                 # only get repos
    #                 c = Chain("user") \
    #                     (login=self._task.name) \
    #                     .get(Chain("repositories") \
    #                              (first=100) \
    #                          .get(Chain("pageInfo") \
    #                               .get("endCursor hasNextPage")) \
    #                          .nodes \
    #                          .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
    #                          .get(Chain("languages")
    #                               (first=100) \
    #                               .nodes \
    #                               .get("name")) \
    #                          .get(Chain("parent")
    #                               .get("projectsUrl")) \
    #                          .get(Chain("licenseInfo")
    #                               .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
    #                          )
    #
    #             return c
    #
    #         c = Chain("user") \
    #             (login=self._task.name)
    #
    #         if has_more_followers:
    #             c = c \
    #                 .get(Chain("followers") \
    #                          (first=100, after=followers_end_cursor) \
    #                      .get(Chain("pageInfo") \
    #                           .get("endCursor hasNextPage")) \
    #                      .nodes \
    #                      .get("login"))
    #
    #         if has_more_following:
    #             c = c \
    #                 .get(Chain("following") \
    #                          (first=100, after=following_end_cursor) \
    #                      .get(Chain("pageInfo") \
    #                           .get("endCursor hasNextPage")) \
    #                      .nodes \
    #                      .get("login"))
    #
    #         if has_more_repos:
    #             c = c \
    #                 .get(Chain("repositories") \
    #                          (first=100, after=repos_end_cursor) \
    #                      .get(Chain("pageInfo") \
    #                           .get("endCursor hasNextPage")) \
    #                      .nodes \
    #                      .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
    #                      .get(Chain("languages")
    #                           (first=100) \
    #                           .nodes \
    #                           .get("name")) \
    #                      .get(Chain("parent")
    #                           .get("projectsUrl")) \
    #                      .get(Chain("licenseInfo")
    #                           .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
    #                      .get(Chain("stargazers") \
    #                               (first=1) \
    #                           .get("totalCount")) \
    #                      .get(Chain("watchers") \
    #                               (first=1) \
    #                           .get("totalCount")) \
    #                      )
    #
    #         if has_more_orgs:
    #             c = c \
    #                 .get(Chain("organizations") \
    #                          (first=100, after=orgs_end_cursor) \
    #                      .get(Chain("pageInfo") \
    #                           .get("endCursor hasNextPage")) \
    #                      .nodes \
    #                      .get("login"))
    #         return c
    #
    #     async def _handle_result():
    #         users = set()
    #         repos = []
    #         nonlocal has_more_followers, has_more_following, \
    #             has_more_repos, has_more_orgs
    #         if has_more_followers:
    #             has_more_followers = data['user'] \
    #                 ['followers']['pageInfo']['hasNextPage']
    #             # noinspection PyTypeChecker
    #             followers_end_cursor = data['user'] \
    #                 ['followers']['pageInfo']['endCursor']
    #             res = self.extract_owners(data['user']
    #                                       ['followers']['nodes'])
    #             users.update(res)
    #
    #         if has_more_following:
    #             has_more_following = data['user'] \
    #                 ['following']['pageInfo']['hasNextPage']
    #             following_end_cursor = data['user'] \
    #                 ['following']['pageInfo']['endCursor']
    #             res = self.extract_owners(data['user']
    #                                       ['following']['nodes'])
    #             users.update(res)
    #
    #         if has_more_repos:
    #             has_more_repos = data['user'] \
    #                 ['repositories']['pageInfo']['hasNextPage']
    #             repos_end_cursor = data['user'] \
    #                 ['repositories']['pageInfo']['endCursor']
    #             res = self.extrack_repos(data['user']
    #                                      ['repositories']['nodes'])
    #             repos.extend(res)
    #
    #         if has_more_orgs:
    #             has_more_orgs = data['user'] \
    #                 ['organizations']['pageInfo']['hasNextPage']
    #             orgs_end_cursor = data['user'] \
    #                 ['organizations']['pageInfo']['endCursor']
    #             res = self.extract_owners(data['user'] \
    #                                           ['organizations']['nodes'],
    #                                       is_org=True)
    #             users.update(res)
    #
    #         if self._task.is_more:
    #             logger.info(f"get users {len(users)} from {self._task.name}")
    #         else:
    #             logger.info(f"get repos {len(repos)} from {self._task.name}")
    #         for i in users:
    #             await self._task_pool.put(i)
    #         await self._store.put(repos)
    #
    #         if not (has_more_followers or
    #                 has_more_following or
    #                 has_more_orgs or
    #                 has_more_repos):
    #             # no more data
    #             return False
    #         return True
    #
    #     chain = _gen_chain(init=True)
    #     while self._running:
    #         try:
    #             raw_data = await self._spider.fetch(chain.to_dict())
    #             if raw_data['data'] is None:
    #                 logger.warn(f"data is None, result = {raw_data}")
    #                 return True
    #             if raw_data['data']['user'] is None:
    #                 return False
    #             data = raw_data['data']
    #         except KeyError:
    #             logger.error(f"result = {raw_data}")
    #             if "abuse" in raw_data['documentation_url']:
    #                 self.handle_abuse()
    #                 return True
    #         except Exception:
    #             logger.error(f"result = {raw_data}")
    #
    #         has_more = await _handle_result()
    #         if not has_more:
    #             # no more data
    #             return True
    #
    def extrack_repos(self, repos: list):
        self._statist.increase_repos(len(repos))
        asyncio.ensure_future(self._store.put(repos))
        
        return repos
    
    def extract_owners(self, owners, is_org=False):
        users = {Task(i, is_org) for i in owners}
        self._statist.increase_user(len(users))
        for i in users:
            asyncio.ensure_future(self._task_pool.put(i))
        return users
    
    def handle_abuse(self):
        logger.info(f"in handle abuse from {self._task.name}")

async def test():
    worker = Worker(BaseTaskProviderProxy(), Store(), Statist())
    await worker.start()
    await asyncio.sleep(10000)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
