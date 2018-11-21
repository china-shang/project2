import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from typing import *
from bs4 import BeautifulSoup as Soup
from base.baseworker import BaseWorker
from gitee.spider import Spider
from gitee.taskproviderproxy import BaseTaskProviderProxy
from gitee.task import Task
from gitee.repos import Repos
from statist import Statist
from datastore import Store

from logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pass


# noinspection PyTypeChecker,PyBroadException
class Worker(BaseWorker):
    def __init__(self, taskspool: BaseTaskProviderProxy,
                 store: Store, statist: Statist,name=""):
        super().__init__(taskspool, store, statist,name=name)
        
        self._name=name
        self._task_pool = taskspool
        self._store = store
        self._statist = statist
        self._spider = Spider()
        self._task: Task = Task("pyinjava")
    
    async def run(self):
        while self._running:
            self._task = await self.get_task()
            logger.info(f"get tasks:{self._task}")
            try:
                await self.handle()
                await self._task_pool.complete(self._task)
                logger.info(f"complete {self._task}")
            except Exception as e:
                logger.error(f"task {self._task.name} error ,mark fail")
                await self._task_pool.fail(self._task)
    async def get_task(self):
        task = await self._task_pool.get()
        if task:
            logger.info(f"get repos task {task.name}")
            return task
        else:
            task = await self._task_pool.get(more=True)
            if task:
                logger.info(f"get users task {task['name']}")
                return task
            else:
                # maybe no task
                logger.warning(f"maybe no task")
                
                return None
        return task
    
    async def handle(self):
        if not self._task:
            logger.warning("no task")
            await asyncio.sleep(5)
        if self._task.is_more:
            logger.info("handle users task")
            await self._handle_more()
        else:
            await self._handle()
    
    async def _handle(self):
        res = await self._spider.fetch(self._task.name)
        repos = self.extract_repos(res)
        self._statist.increase_repos(len(repos))
        logger.info(f"get repos {len(repos)}")
        await self._store.put(repos)
    
    async def _handle_more(self):
        res = await self._spider.fetch(self._task.name, project=False)
        users = self.extract_owners(res)
        for i in users:
            await self._task_pool.put(Task(i))
        self._statist.increase_user(len(users))
        logger.info(f"get {len(users)} users from {self._task.name}")
    
    def extract_repos(self, repos: List[Soup]):
        if not repos or len(repos) == 0:
            return []
        # no repos
        
        repos_set = set()
        for sp in repos:
            # sp is "div.project"
            try:
                if len(sp.select('.main-pro-name ')) > 0:
                    # if fork
                    author_sp = sp.select_one(".main-pro-name .author")
                    nickauthor = author_sp['title']
                    author = author_sp['href'][1:]
                    
                    repo_sp = sp.select_one(".main-pro-name .repository")
                    name = repo_sp['title']
                    
                    forkfrom = sp.select_one(".fork-pro-name .repository")['href']
                    isfork = True
                else:
                    # not be fork
                    author_sp = sp.select_one(".author")
                    nickauthor = author_sp['title']
                    author = author_sp['href'][1:]
                    
                    repo_sp = sp.select_one(".repository")
                    name = repo_sp['title']
                    
                    forkfrom = None
                    isfork = False
                if sp.select_one(".label"):
                    lang = sp.select_one(".label").text
                else:
                    lang = ""
                
                if sp.select_one(".icon-recommended"):
                    viplevel = "recommended"
                elif sp.select_one(".gvp-label"):
                    viplevel = "vip"
                else:
                    viplevel = "none"
                    
                desc = sp.select_one(".description").text
                updatetime = sp.select_one(".create-time span").text
                watch = int(sp.select(".watch a")[-1].text)
                star = int(sp.select(".star a")[-1].text)
                fork_sp = sp.select(".fork a")
                if fork_sp and len(fork_sp) >= 2:
                    fork = int(sp.select(".fork a")[-1].text)
                else:
                    fork = 0
            except Exception:
                print(sp)
                exit(3)
            
            # print(name,nickauthor,author,lang,viplevel,desc,updatetime,watch,
            #       star,fork,isfork,forkfrom)
            
            repos = Repos(name, nickauthor, author, lang, viplevel, desc, updatetime, watch,
                          star, fork, isfork, forkfrom)
            repos_set.add(repos)
        return repos_set
    
    def extract_owners(self, owners: List[Soup]):
        if not owners or len(owners) == 0:
            return []
        # no owners
        owners_set = set()
        for sp in owners:
            owners_set.add(sp['href'][1:])
        return owners_set
    
    def handle_abuse(self):
        logger.info(f"in handle abuse")


def extract_repos(repos: List[Soup]):
    if not repos or len(repos) == 0:
        return 0
    # no repos
    
    repos_set = set()
    for sp in repos:
        # sp is "div.project"
        if len(sp.select('.main-pro-name ')) > 0:
            # if fork
            author_sp = sp.select_one(".main-pro-name .author")
            nickauthor = author_sp['title']
            author = author_sp['href'][1:]
            
            repo_sp = sp.select_one(".main-pro-name .repository")
            name = repo_sp['title']
            
            forkfrom = sp.select_one(".fork-pro-name .repository")['href']
            isfork = True
        else:
            author_sp = sp.select_one(".author")
            nickauthor = author_sp['title']
            author = author_sp['href'][1:]
            
            repo_sp = sp.select_one(".repository")
            name = repo_sp['title']
            
            forkfrom = None
            isfork = False
        if sp.select_one(".label"):
            lang = sp.select_one(".label").text
        else:
            lang = ""
        
        if sp.select_one(".icon-recommended"):
            viplevel = "recommended"
        elif sp.select_one(".gvp-label"):
            viplevel = "vip"
        else:
            viplevel = "none"
        desc = sp.select_one(".description").text
        
        updatetime = sp.select_one(".create-time span").text
        
        watch = int(sp.select(".watch a")[-1].text)
        star = int(sp.select(".star a")[-1].text)
        fork_sp = sp.select(".fork a")
        if fork_sp and len(fork_sp) >= 2:
            fork = int(sp.select(".fork a")[-1].text)
        else:
            fork = 0
        
        # print(name,nickauthor,author,lang,viplevel,desc,updatetime,watch,
        #       star,fork,isfork,forkfrom)
        
        repos = Repos(name, nickauthor, author, lang, viplevel, desc, updatetime, watch,
                      star, fork, isfork, forkfrom)
        repos_set.add(repos)
    return repos_set

def extract_owners(owners: List[Soup]):
    if not owners or len(owners) == 0:
        return
    # no owners
    owners_set = set()
    for sp in owners:
        owners_set.add(sp['href'][1:])
    return owners_set


async def test_extract():
    with open("projects.txt") as fp:
        text = fp.read()
    res = []
    sp = Soup(text, "lxml")
    sp = sp.select("div.project")
    res.extend([i for i in sp])
    res = extract_repos(res)
    logger.info(f"res={res}")
    
    with open("users.txt", "r") as fp:
        text = fp.read()
    
    sp = Soup(text, "lxml")
    l = []
    l = sp.select(".user-list-item .header a")
    res = extract_owners(l)
    logger.info(f"res={res}")


async def test():
    worker = Worker(BaseTaskProviderProxy(), Store(), Statist())
    await worker.start()
    await asyncio.sleep(10000)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
