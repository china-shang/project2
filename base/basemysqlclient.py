import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

import aiomysql
import asyncio
from typing import *
from config import Config


class BaseMysqlClient(object):
    """
    communication with mysql server and provide api for upper layer
    only be responsible for pure data, not task
    """
    create_body = """
   CREATE TABLE IF NOT EXISTS `gitee` (
  `name` VARCHAR(100) NOT NULL,
  `repos_done` BOOL DEFAULT FALSE,
  `repos_doing` BOOL DEFAULT FALSE,
  `users_done` BOOL DEFAULT FALSE  ,
  `users_doing` BOOL DEFAULT FALSE,
  `users_done_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `repos_done_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `users_doing_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `repos_doing_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`name`),
  INDEX `repos_done_idx` (`repos_done`),
  INDEX `users_done_idx` (`users_done`),
  INDEX `repos_doing_idx` (`repos_doing`),
  INDEX `users_doing_idx` (`users_doing`)
    );
    """
    
    sel_body = f"select name from gitee where repos_doing!=True and repos_done!=True LIMIT 10;"
    users_sel_body = f"select name from gitee where users_doing!=True and users_done!=True LIMIT 10;"
    update_body = '''update gitee set repos_doing_time=current_timestamp(),repos_doing=True
         where name in {};
        '''
    users_update_body = '''update gitee set users_doing_time=current_timestamp(),users_doing=True
         where name in {};
        '''
    fail_body = '''update gitee set repos_doing=False
         where name in {};
        '''
    users_fail_body = '''update gitee set users_doing=False
         where name in {};
        '''
    complete_body = '''update gitee set repos_done_time=current_timestamp(),repos_done=True
         where name in {};
        '''
    users_complete_body = '''update gitee set users_done_time=current_timestamp(),users_done=True
         where name in {};
        '''
    check_body = 'SELECT name FROM gitee where `name` in {};'
    mark_fail_body=' update gitee set users_doing=0,repos_doing=0;'
    
    def __init__(self, addr="localhost", port=3306,
                 config=Config.init_mysql_config(), autocommit=False):
        """
        
        :param addr:
        :param port:
        :param config:
        :param autocommit:
        """
        self.addr = addr
        self.port = port
        self._config = config
        self._autocommit = autocommit
        self._pool: aiomysql.Pool = None
        # self._pool=aiomysql.Pool()
    
    async def connection(self):
        """
        connection with mysql server
        :return:None
        """
        self._pool = await aiomysql.create_pool(
            **self._config,
            autocommit=self._autocommit,
        )
    
    @staticmethod
    def tostr(data: tuple)->str:
        """
        change list or tuple to str use for sql
        :param data:
        :return:
        """
        t = ""
        for i in data:
            t = f"{t}'{i}',"
        t = f"({t[:-1]})"
        return t
    
    async def remain(self) -> int:
        pass
    
    async def get(self, users=False)->set:
        if users:
            result=await self.get_users()
        else:
            async with self._pool.acquire() as con:
                async with con.cursor() as cur:
                    con: aiomysql.Connection
                    cur: aiomysql.Cursor
                    await cur.execute(self.sel_body)
                    res = await cur.fetchall()
                    result = {i[0] for i in res}
                    if len(result) > 0:
                        await cur.execute(
                            self.update_body.format(self.tostr(result)))
        # print(f"result={result}")
                
        return result
    
    async def get_users(self):
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                con: aiomysql.Connection
                cur: aiomysql.Cursor
                await cur.execute(self.users_sel_body)
                res = await cur.fetchall()
                result = {i[0] for i in res}
                if len(result) > 0:
                    await cur.execute(
                        self.users_update_body.format(self.tostr(result)))
                return result
    async def get_users_count(self):
        pass
    
    async def get_users_remain(self):
        pass
    
    async def put(self, data: set):
        if not data or len(data) < 0:
            return
        repeat = await self._check_exist(data)
        data.difference_update(repeat)
        
        if len(data) == 0:
            return
        
        values = ""
        for u in data:
            values = f"{values}('{u}'),"
        values = values[:-1]
        
        body = f"INSERT INTO gitee (`name`) VALUES {values};"
        # print(f"put body={body}")
        
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(body)
    
    async def _check_exist(self, data: set):
        if not data or len(data) < 0:
            return set()
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(self.check_body.format(self.tostr(data)))
                res = await cur.fetchall()
                return {i[0] for i in res}
    
    async def complete(self, data: Set[Tuple[str,bool]]):
        data1={i for i in data if i[1]}
        await self.complete_users(data1)
        #complete user_task
        data.difference_update(data1)
        # remove user_task from data
        
        if not data or len(data) < 0:
            return
        #no data
        data={i[0] for i in data}
        #extract name from data
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(
                    self.complete_body.format(self.tostr(data)))
                
    async def complete_users(self,data: Set[Tuple[str,bool]]):
        if not data or len(data) < 0:
            return
        data={i[0] for i in data}
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(
                    self.users_complete_body.format(self.tostr(data)))

    async def fail(self, data: Set[Tuple[str,bool]]):
        data1={i for i in data if i[1]}
        await self.fail_users(data1)
        #fail user_task
        data.difference_update(data1)
        # remove user_task from data
    
        if not data or len(data) < 0:
            return
        #no data
        data={i[0] for i in data}
        #extract name from data
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(
                    self.fail_body.format(self.tostr(data)))

    async def fail_users(self,data: Set[Tuple[str,bool]]):
        if not data or len(data) < 0:
            return
        data={i[0] for i in data}
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(
                    self.users_fail_body.format(self.tostr(data)))
                
    async def close(self):
        await self._pool.close()
    
    async def create_table(self):
        async with self._pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(self.create_body)
                res = await cur.fetchall()
                print(f"res={res}")
                
    async def remain(self):
        pass

async def test():
    client = BaseMysqlClient(autocommit=True)
    await client.connection()
    # await client.create_table()
    await client.put({"s324", "df", "sdji", "sdjf"})
    result = await client.get()
    print(result)
    await client.complete(result)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
