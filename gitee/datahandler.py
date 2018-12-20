import json
import glob

{'name': 'mars',
 'url': 'https://github.com/king6cong/mars',
 'description': 'Mars is a cross-platform network component  developed by WeChat.',
 'updatedAt': '2018-11-21T03:11:01Z',
 'projectsUrl': 'https://github.com/king6cong/mars/projects',
 'forkCount': 0,
 'isFork': True,
 'languages': {'nodes': [{'name': 'C++'}, {'name': 'C'}, {'name': 'Makefile'}, {'name': 'Perl'}, {'name': 'Assembly'}, {'name': 'M4'}, {'name': 'Batchfile'}, {'name': 'Shell'}, {'name': 'Objective-C'}, {'name': 'Objective-C++'}, {'name': 'C#'}, {'name': 'Python'}, {'name': 'Java'}, {'name': 'Pawn'}]},
 'parent': {'projectsUrl': 'https://github.com/Tencent/mars/projects'},
 'licenseInfo': {'name': 'Other', 'nickname': None, 'pseudoLicense': True, 'implementation': None, 'description': None, 'spdxId': 'NOASSERTION'} ,
 'stargazers': {'totalCount': 0},
 'watchers': {'totalCount': 1}}
class Model(dict):
    def __init__(self,data:dict,src="github",):
        super().__init__(data)
        if src=="github":
            self._handle_github()
        else:
            self._handle_gitee()
    
    def _handle_github(self):
        self.pop('projectsUrl')
        self.setdefault("forks",self.get('forkCount'))
        langs=self.pop("languages").get("nodes")
        if len(langs)==0:
            self.setdefault('langs',[])
        else:
            new_langs=[]
            for i in langs:
                new_langs.append(i['name'])
            self.setdefault('langs',new_langs)
            
        if self.get("isFork"):
            parent=self.pop("parent")['projectsUrl'][:-13]
            self.setdefault("parent",parent)
        else:
            self.setdefault("parent",None)
            
        license=self.pop("licenseInfo")
        if license:
            self.setdefault("license",license.get("nickname",None))

        stars=self.pop('stargazers',{})
        self.setdefault("stars",stars.get("totalCount",0))

        watchers=self.pop('watchers',{})
        self.setdefault("watchers",watchers.get("totalCount",0))
        
        forks=self.pop('forkCount',0)
        self.setdefault("forks",forks)
        
        self.setdefault("src","github")

    def _handle_gitee(self):
        {'name': 'mars',
         'url': 'https://github.com/king6cong/mars',
         'description': 'Mars is a cross-platform network component  developed by WeChat.',
         'updatedAt': '2018-11-21T03:11:01Z',
         'forks': 0,
         'isFork': True,
         'languages': [ 'C++',"C" ],
         'parent':  'https://github.com/Tencent/mars/projects',
         'license': "GPL3" ,
         'stars': {'totalCount': 0},
         'watchers': {'totalCount': 1}}

        {'name': 'JXPC', 'nickname': 'god', 'author': 'god0', 'lang': 'NodeJS', 'viplevel': 'none',
         'desc': '\n基于nodej的教学质量评测平台\n', 'updatetime': '1个月前', 'watch': 0, 'star': 0, 'fork': 7, 'isfork': True,
         'forkfrom': '/Hiraeth/JXPC'}

        from_=self.pop("nickname")
        from_=self.pop("viplevel")
        name=self.get("name")
        author=self.pop("author")
        
        # url=f"https://gitee.com/{author}/{name}"
        # self.setdefault("url",url)
        
        self.setdefault("description",self.pop("desc"))
        self.setdefault("updatedAt",self.pop("updatetime"))
        self.setdefault("forks",self.pop("fork"))
        self.setdefault("stars",self.pop("star"))
        self.setdefault("watchers",self.pop("watch"))
        isFork=self.pop("isfork",False)
        self.setdefault("isFork",isFork)
        if isFork:
            from_=self.pop("forkfrom")
            parent_url=f"https://gitee.com{from_}"
            self.setdefault("parent",parent_url)
        else:
            self.setdefault("parent",None)
        self.setdefault('license',None)
        self.setdefault('src',"gitee")
        
        lang=self.pop("lang",None)
        if lang:
            self.setdefault('langs',[lang])
        # print(self.get("updatedAt"))
            
        
        

def load(s) -> list:
    l=[]
    try:
        l=json.loads(s)
    except json.JSONDecodeError as e:
        l.extend(load(s[:e.pos]))
        l.extend(load(s[e.pos:]))
    
    return l

def test():
    file=glob.glob("./data/repos15*")[0]
    # print(file)
    with open(file) as fp:
        l=load(fp.read())
        for i in l:
            m=Model(data=i,src="gitee")
            # print(m)




    iile=glob.glob("./data/repos15*")[0]
    # print(file)
    with open(file) as fp:
        l=load(fp.read())
        for i in l:
            m=Model(data=i,src="gitee")
            print(m)


if __name__ == '__main__':
    test()
    
