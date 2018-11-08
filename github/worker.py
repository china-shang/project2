import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.baseworker import BaseWorker
from github.chain import Chain
from github.spider import Spider
from github.taskproviderproxy import BaseTaskProviderProxy
from github.task import Task
from statistic import Statist
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
                 store: Store, statist: Statist):
        super().__init__(taskspool,store,statist)
        
        self._spider = Spider()
        self._task = Task("")
    
    async def run(self):
        while self._running:
            self._task = self.get_task()
            await self.handle()
    
    async def handle(self):
        await self._handle()
    
    async def _handle(self):
        if self._task.is_org:
            await self._handle_org()
        else:
            try:
                await self._handle_user()
            except TaskTypeError:
                await self._handle_org()
    #TODO get more attr like forked
    
    async def _handle_org(self):
        if self._task.is_more:
            has_more_members = True
            has_more_repos = False
            # only fetch users
        else:
            has_more_members = False
            has_more_repos = True
            # only fetch repos

        # noinspection PyUnresolvedReferences
        def _gen_chain(init=False):
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
                             .get('name', 'url', 'description',
                                  'updatedAt', 'projectsUrl', 'forkCount') \
                             .get(Chain("languages")
                                  (first=100) \
                                  .nodes \
                                  .get("name"))
                             .get(Chain("stargazers") \
                                      (first=1) \
                                  .get("totalCount")) \
                             .get(Chain("watchers") \
                                      (first=1) \
                                  .get("totalCount"))
                             )
                return chain
            
            chain = Chain("organization") \
                (login=self._task.name)
            
            if has_more_members:
                chain = chain.get(Chain("members") \
                                      (first=100,
                                       after=members_end_cursor) \
                                  .get(Chain("pageInfo") \
                                       .get("endCursor hasNextPage")) \
                                  .nodes \
                                  .get("login"))
            
            if has_more_repos:
                chain = chain \
                    .get(Chain("repositories") \
                             (first=100, after=repos_end_cursor) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get('name', 'url', 'description', 'updatedAt',
                              'projectsUrl', 'forkCount') \
                         .get(Chain("languages")
                              (first=100) \
                              .nodes \
                              .get("name"))
                         .get(Chain("stargazers") \
                                  (first=1) \
                              .get("totalCount")) \
                         .get(Chain("watchers") \
                                  (first=1) \
                              .get("totalCount")) \
                         )
            return chain
        
        def _handle_result():
            if has_more_members:
                has_more_members = data['organization'] \
                    ['members']['pageInfo']['hasNextPage']
                members_end_cursor = data['organization'] \
                    ['members']['pageInfo']['endCursor']
                self.extract_owners(data['organization'] \
                                        ['members']['nodes'])
            
            if has_more_repos:
                has_more_repos = data['organization'] \
                    ['repositories']['pageInfo']['hasNextPage']
                repos_end_cursor = data['organization'] \
                    ['repositories']['pageInfo']['endCursor']
                self.extrack_repos(data['organization'] \
                                       ['repositories']['nodes'])
        
        
        chain = _gen_chain(init=True)
        while self._running:
            try:
                raw_data = await self._spider.fetch(chain.to_dict())
                if raw_data['data'] is None:
                    logger.warn(f"data is None, result = {raw_data}")
                    return None
                if raw_data['data']['user'] is None:
                    return False
                data = raw_data['data']
            except KeyError:
                logger.error(f"result = {raw_data}")
                if "abuse" in raw_data['documentation_url']:
                    self.handle_abuse()
                    return None
            except Exception:
                logger.error(f"result = {raw_data}")
            
            _handle_result()
            if not (has_more_members or
                    has_more_repos):
                # no more data
                break
    
    async def _handle_user(self):
        if self._task.is_more:
            has_more_followers = True
            has_more_following = True
            has_more_orgs = True
            has_more_repos = False
            # only fetch users
        else:
            has_more_followers = False
            has_more_following = False
            has_more_orgs = False
            has_more_repos = True
            # only fetch repos

        # noinspection PyUnresolvedReferences
        def _gen_chain(init=False):
            if init:
                if self._task.is_more:
                    # only get users
                    c = Chain("user") \
                        (login=self._task.name)\
                        .get(Chain("repositories")
                                 (first=100)
                             .get(Chain("pageInfo")
                                  .get("endCursor hasNextPage"))
                             .nodes
                             .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount') \
                             .get(Chain("languages")
                                  (first=100)
                                  .nodes
                                  .get("name")))
                else:
                    # only get repos
                    c = Chain("user") \
                        (login=self._task.name) \
                        .get(Chain("repositories") \
                                 (first=100) \
                             .get(Chain("pageInfo") \
                                  .get("endCursor hasNextPage")) \
                             .nodes \
                             .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount') \
                             .get(Chain("languages")
                                  (first=100) \
                                  .nodes \
                                  .get("name")))
                
                return c
            
            c = Chain("user") \
                (login=self._task.name)
            
            if has_more_followers:
                c = c \
                    .get(Chain("followers") \
                             (first=10, after=followers_end_cursor) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get("login"))
            
            if has_more_following:
                c = c \
                    .get(Chain("following") \
                             (first=10, after=following_end_cursor) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get("login"))
            
            if has_more_repos:
                c = c \
                    .get(Chain("repositories") \
                             (first=100, after=repos_end_cursor) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get('name', 'url', 'description', 'updatedAt', 'projectsUrl', 'forkCount') \
                         .get(Chain("languages")
                              (first=100) \
                              .nodes \
                              .get("name"))
                         .get(Chain("stargazers") \
                                  (first=1) \
                              .get("totalCount")) \
                         .get(Chain("watchers") \
                                  (first=1) \
                              .get("totalCount")) \
                         )
            
            if has_more_orgs:
                c = c \
                    .get(Chain("organizations") \
                             (first=10, after=orgs_end_cursor) \
                         .get(Chain("pageInfo") \
                              .get("endCursor hasNextPage")) \
                         .nodes \
                         .get("login"))
            return c
        
        def _handle_result():
            if has_more_followers:
                has_more_followers = data['user']\
                ['followers']['pageInfo']['hasNextPage']
                # noinspection PyTypeChecker
                followers_end_cursor = data['user']\
                ['followers']['pageInfo']['endCursor']
                self.extract_owners(data['user']
                                    ['followers']['nodes'])
            
            if has_more_following:
                has_more_following = data['user']\
                ['following']['pageInfo']['hasNextPage']
                following_end_cursor = data['user']\
                ['following']['pageInfo']['endCursor']
                self.extract_owners(data['user']
                                    ['following']['nodes'])
            
            if has_more_repos:
                has_more_repos = data['user']\
                ['repositories']['pageInfo']['hasNextPage']
                repos_end_cursor = data['user']\
                ['repositories']['pageInfo']['endCursor']
                self.extrack_repos(data['user']
                                   ['repositories']['nodes'])
            
            if has_more_orgs:
                has_more_orgs = data['user']\
                ['organizations']['pageInfo']['hasNextPage']
                orgs_end_cursor = data['user']\
                ['organizations']['pageInfo']['endCursor']
                self.extract_owners(data['user']\
                                    ['organizations']['nodes'],
                                    is_org=True)
        
        chain = _gen_chain(init=True)
        while self._running:
            try:
                raw_data = await self._spider.fetch(chain.to_dict())
                if raw_data['data'] is None:
                    logger.warn(f"data is None, result = {raw_data}")
                    return None
                if raw_data['data']['user'] is None:
                    return False
                data = raw_data['data']
            except KeyError:
                logger.error(f"result = {raw_data}")
                if "abuse" in raw_data['documentation_url']:
                    self.handle_abuse()
                    return None
            except Exception:
                logger.error(f"result = {raw_data}")
            
            _handle_result()
            if not (has_more_followers or
                    has_more_following or
                    has_more_orgs or
                    has_more_repos):
                # no more data
                break
    
    def extrack_repos(self, repos: list):
        repos = set(repos)
        self._store.put(repos)
        return len(repos)
    
    def extract_owners(self, owners, is_org=False):
        owners = {Task(i["login"], is_org) for i in owners}
        self._task_pool.put(owners)
        return len(owners)

    def handle_abuse(self):
        logger.info(f"in handle abuse")
