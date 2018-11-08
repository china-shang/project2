
# load config
import json
import os

class Config(object):
    mysqlconfig=None
    path="/home/zh/PycharmProjects/project"
    @classmethod
    def mysql_config(cls):
        if not cls.mysqlconfig:
            path=os.path.join(cls.path,"mysql.json")
            path=os.path.abspath(path)
            with open(path,"r") as fp:
                cls.mysqlconfig=json.load(fp)
                
        return cls.mysqlconfig
    
    @classmethod
    def init(cls):
        cls.mysql_config()

Config.init()

