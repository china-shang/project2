from github.spider import Spider
from github.task import Task
from github.chain import Chain
from base.baselooper import BaseLooper
import asyncio

from logger import get_logger

logger = get_logger(__name__)


class TaskHander(BaseLooper):
    def __init__(self, task: Task, spider: Spider):
        super().__init__()
        self._task = task
        self._spider = spider
        
        self._init_stat()

    async def start(self):
        return await super().start()

    async def stop(self):
        await self._spider.close()
        return await super().stop()

    async def run(self):
        return await super().run()

    def _init_stat(self):
        self._has_more_members = False
        self._has_more_repos = False
        
        self._has_more_followers = False
        self._has_more_following = False
        self._has_more_orgs = False
        self._has_more = False
        
        self._orgs_end_cursor = ""
        self._members_end_cursor = ""
        self._repos_end_cursor = ""
        self._followers_end_cursor = ""
        self._following_end_cursor = ""
        
        self._repos = []
        self._users = set()
        self._orgs = set()
    
    def get_result(self) -> tuple:
        """
        get current result
        :return repos and users:
        """
        return self._repos, self._users,self._orgs
    
    async def handle(self, task: Task = None):
        if task:
            self._task = task
        self._init_stat()
        if self._task.is_org:
            is_org=await self._handle_org()
            if not is_org:
                await self._handle_user()
        else:
            is_usr = await self._handle_user()
            if not is_usr:
                await self._handle_org()
        return self.get_result()
    
    def _gen_user_chain(self, init=False):
        if init:
            if self._task.is_more:
                # only get users
                c = Chain("user") \
                    (login=self._task.name) \
                    .get(Chain("followers")
                         (first=100) \
                         .get(Chain("pageInfo")
                              .get("endCursor hasNextPage"))
                         .nodes
                         .get("login")) \
                    .get(Chain("following")
                         (first=100)
                         .get(Chain("pageInfo")
                              .get("endCursor hasNextPage"))
                         .nodes
                         .get("login")) \
                    .get(Chain("organizations")
                         (first=100)
                         .get(Chain("pageInfo")
                              .get("endCursor hasNextPage"))
                         .nodes
                         .get("login"))
            else:
                # only get repos
                c = Chain("user") \
                    (login=self._task.name) \
                    .get(Chain("repositories") \
                             (first=100) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
                         .get(Chain("languages")
                              (first=100) \
                              .nodes \
                              .get("name")) \
                         .get(Chain("parent")
                              .get("projectsUrl")) \
                         .get(Chain("licenseInfo")
                              .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
                         )
            
            return c
        
        c = Chain("user") \
            (login=self._task.name)
        
        if self._has_more_followers:
            c = c \
                .get(Chain("followers") \
                         (first=100, after=self._followers_end_cursor) \
                     .get(Chain("pageInfo") \
                          .get("endCursor hasNextPage")) \
                     .nodes \
                     .get("login"))
        
        if self._has_more_following:
            c = c \
                .get(Chain("following") \
                         (first=100, after=self._following_end_cursor) \
                     .get(Chain("pageInfo") \
                          .get("endCursor hasNextPage")) \
                     .nodes \
                     .get("login"))
        
        if self._has_more_repos:
            c = c \
                .get(Chain("repositories") \
                         (first=100, after=self._repos_end_cursor) \
                     .get(Chain("pageInfo") \
                          .get("endCursor hasNextPage")) \
                     .nodes \
                     .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
                     .get(Chain("languages")
                          (first=100) \
                          .nodes \
                          .get("name")) \
                     .get(Chain("parent")
                          .get("projectsUrl")) \
                     .get(Chain("licenseInfo")
                          .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
                     .get(Chain("stargazers") \
                              (first=1) \
                          .get("totalCount")) \
                     .get(Chain("watchers") \
                              (first=1) \
                          .get("totalCount")) \
                     )
        
        if self._has_more_orgs:
            c = c \
                .get(Chain("organizations") \
                         (first=100, after=self._orgs_end_cursor) \
                     .get(Chain("pageInfo") \
                          .get("endCursor hasNextPage")) \
                     .nodes \
                     .get("login"))
        return c
    
    def _gen_org_chain(self, init=False):
        if init:
            if self._task.is_more:
                chain = Chain("organization") \
                    (login=self._task.name) \
                    .get(Chain("members") \
                             (first=100) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get("login"))
            else:
                chain = Chain("organization") \
                    (login=self._task.name) \
                    .get(Chain("repositories") \
                             (first=100) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
                         .get(Chain("languages")
                              (first=10) \
                              .nodes \
                              .get("name")) \
                         .get(Chain("parent")
                              .get("projectsUrl")) \
                         .get(Chain("licenseInfo")
                              .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
                         .get(Chain("stargazers") \
                                  (first=1) \
                              .get("totalCount")) \
                         .get(Chain("watchers") \
                                  (first=1) \
                              .get("totalCount")) \
                         )
            return chain
        
        chain = Chain("organization") \
            (login=self._task.name)
        
        if self._has_more_members:
            chain = chain.get(Chain("members") \
                                  (first=100,
                                   after=self._members_end_cursor) \
                              .get(Chain("pageInfo") \
                                   .get("endCursor hasNextPage")) \
                              .nodes \
                              .get("login"))
        
        if self._has_more_repos:
            chain = chain \
                .get(Chain("repositories") \
                         (first=100, after=self._repos_end_cursor) \
                     .get(Chain("pageInfo") \
                          .get("endCursor hasNextPage")) \
                     .nodes \
                     .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount', 'isFork') \
                     .get(Chain("languages")
                          (first=100) \
                          .nodes \
                          .get("name")) \
                     .get(Chain("parent")
                          .get("projectsUrl")) \
                     .get(Chain("licenseInfo")
                          .get("name", "nickname", "pseudoLicense", "implementation", "description", "spdxId"))
                     .get(Chain("stargazers") \
                              (first=1) \
                          .get("totalCount")) \
                     .get(Chain("watchers") \
                              (first=1) \
                          .get("totalCount")) \
                     )
        return chain
    
    async def _handle_org(self):
        if self._task.is_more:
            self._has_more_members = True
            self._has_more_repos = False
            # only fetch users
        else:
            self._has_more_members = False
            self._has_more_repos = True
            # only fetch repos
        
        chain = self._gen_org_chain(init=True)
        while self._running:
            try:
                raw_data = await self._spider.fetch(chain.to_dict())
                if raw_data['data'] is None:
                    logger.warning(f" data is None ,result = {raw_data}")
                    return True
                if not raw_data['data']['organization']:
                    # logger.warning(f"result = {raw_data}")
                    logger.warning(f"{self._task.name} is org.")
                    return False
                data = raw_data['data']
            except KeyError:
                logger.error(f"result = {raw_data}")
                if "abuse" in raw_data['documentation_url']:
                    self.handle_abuse()
                    return True
            except Exception:
                logger.error(f"result = {raw_data}")
            
            await self._handle_org_result(data)
            if not self._has_more:
                # no more data
                return True
            chain = self._gen_org_chain()
    
    async def _handle_user(self):
        if self._task.is_more:
            # only fetch users
            self._has_more_followers = True
            self._has_more_following = True
            self._has_more_orgs = True
            self._has_more_repos = False
        else:
            # only fetch repos
            self._has_more_followers = False
            self._has_more_following = False
            self._has_more_orgs = False
            self._has_more_repos = True
        chain = self._gen_user_chain(init=True)
        while self._running:
            try:
                raw_data = await self._spider.fetch(chain.to_dict())
                if raw_data['data'] is None:
                    logger.warn(f"data is None, result = {raw_data}")
                    return True
                if raw_data['data']['user'] is None:
                    return False
                data = raw_data['data']
            except KeyError:
                logger.error(f"result = {raw_data}")
                if "abuse" in raw_data['documentation_url']:
                    self.handle_abuse()
                    return True
            except Exception:
                logger.error(f"result = {raw_data}")
            
            await self._handle_user_result(data)
            chain = self._gen_user_chain()
            if not self._has_more:
                # no more data
                return True
    
    async def _handle_user_result(self, data):
        users = set()
        repos = []
        if self._has_more_followers:
            self._has_more_followers = data['user'] \
                ['followers']['pageInfo']['hasNextPage']
            # noinspection PyTypeChecker
            self._followers_end_cursor = data['user'] \
                ['followers']['pageInfo']['endCursor']
            res=data['user']['followers']['nodes']
            users.update({i['login'] for i in res})
        
        if self._has_more_following:
            self._has_more_following = data['user'] \
                ['following']['pageInfo']['hasNextPage']
            self._following_end_cursor = data['user'] \
                ['following']['pageInfo']['endCursor']
            res = data['user']['following']['nodes']
            users.update({i['login'] for i in res})
        
        if self._has_more_repos:
            self._has_more_repos = data['user'] \
                ['repositories']['pageInfo']['hasNextPage']
            self._repos_end_cursor = data['user'] \
                ['repositories']['pageInfo']['endCursor']
            res = data['user']['repositories']['nodes']
            repos.extend(res)
        
        if self._has_more_orgs:
            self._has_more_orgs = data['user'] \
                ['organizations']['pageInfo']['hasNextPage']
            self._orgs_end_cursor = data['user'] \
                ['organizations']['pageInfo']['endCursor']
            org_res = data['user']['organizations']['nodes']
            self._orgs.update({i['login'] for i in org_res})
        
        if self._task.is_more:
            logger.info(f"get users {len(users)} from {self._task.name}")
        else:
            logger.info(f"get repos {len(repos)} from {self._task.name}")
        
        self._users.update(users)
        self._repos.extend(repos)
        if not (self._has_more_followers or
                self._has_more_following or
                self._has_more_orgs or
                self._has_more_repos):
            # no more data
            self._has_more = False
        else:
            self._has_more = True
    
    async def _handle_org_result(self, data):
        
        users = set()
        repos = []
        if self._has_more_members:
            self._has_more_members = data['organization'] \
                ['members']['pageInfo']['hasNextPage']
            self._members_end_cursor = data['organization'] \
                ['members']['pageInfo']['endCursor']
            res = data['organization']['members']['nodes']
            users.update({i['login'] for i in res})
        
        if self._has_more_repos:
            self._has_more_repos = data['organization'] \
                ['repositories']['pageInfo']['hasNextPage']
            self._repos_end_cursor = data['organization'] \
                ['repositories']['pageInfo']['endCursor']
            res = data['organization']['repositories']['nodes']
            repos.extend(res)
        
        if self._task.is_more:
            logger.info(f"get users {len(users)} from {self._task.name}")
        else:
            logger.info(f"get repos {len(repos)} from {self._task.name}")
        
        self._users.update(users)
        self._repos.extend(repos)
        if not (self._has_more_members or self._has_more_repos):
            logger.info(f"{self._task.name} has done")
            self._has_more = False
        else:
            self._has_more = True
    
    def handle_abuse(self):
        logger.error("handle abuse")


async def test():
    t=Task('tschottdorf',is_org=True,more=True)
    handler=TaskHander(None,Spider())
    await handler.start()
    res=await handler.handle(t)
    print(res)

if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
