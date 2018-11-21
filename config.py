
# load config
import json
import os

class Config(object):
    mysqlconfig=None
    githubtoken=None
    path="/home/zh/PycharmProjects/project"
    @classmethod
    def init_mysql_config(cls):
        if not cls.mysqlconfig:
            path=os.path.join(cls.path,"mysql.json")
            path=os.path.abspath(path)
            with open(path,"r") as fp:
                cls.mysqlconfig=json.load(fp)
                
        return cls.mysqlconfig

    @classmethod
    def _init_gihtub_token(cls):
        if not cls.githubtoken:
            path=os.path.join(cls.path,"token.json")
            path=os.path.abspath(path)
            with open(path,"r") as fp:
                cls.githubtoken=json.load(fp)
    
        return cls.githubtoken
    
    @classmethod
    def init(cls):
        cls.init_mysql_config()
        cls._init_gihtub_token()

Config.init()

def test():
    print(f"toekn={Config.githubtoken}")
    
if __name__ == '__main__':
    test()

