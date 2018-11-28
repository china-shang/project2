
# load config
import json
import os

class Config(object):
    mysqlconfig=None
    githubtoken=None
    nodesconfig=None
    nodeconfig=None
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
    def init_node_config(cls):
        if not cls.nodeconfig:
            path=os.path.join(cls.path,"node.json")
            path=os.path.abspath(path)
            with open(path,"r") as fp:
                cls.nodeconfig=json.load(fp)
                
        return cls.nodeconfig
    @classmethod
    def init_nodes_config(cls):
        if not cls.nodesconfig:
            path=os.path.join(cls.path,"nodes.json")
            path=os.path.abspath(path)
            with open(path,"r") as fp:
                cls.nodesconfig=json.load(fp)
                
        return cls.nodesconfig
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
        cls.init_node_config()
        cls.init_nodes_config()

Config.init()

def test():
    print(f"token={Config.githubtoken}")
    print(f"node={Config.nodesconfig['github']}")
    print(f"node={Config.nodeconfig['github']}")
    
if __name__ == '__main__':
    test()

