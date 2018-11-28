import jinja2

loader = jinja2.FileSystemLoader("/home/zh/.WebstormProjects/untitled1")
env = jinja2.Environment(loader=loader)
tmp = env.get_template("repos_li.html")
print(tmp.render(repos=[{"name": "name1",
                         "user": "user1",
                         "src": "github",
                         "url": "www.baidu.com/name/user1",
                         "desr": "this is description",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         },
                        {"name": "name2",
                         "user": "user2",
                         "src": "github",
                         "url": "www.baidu.com/name/user2",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         }
                        ]))
#
# tmp = env.get_template("pages.html")
# print(tmp.render(page={"start": 4, "end": 11, "cur": 6, "url": ['1', '3', '4', '5']}))
#
tmp=env.get_template("main1.html")
with open("main.html","w") as fp:
   s=tmp.render(repos=[{"name": "name1",
                         "user": "user1",
                         "src": "github",
                         "url": "www.baidu.com/name/user1",
                         "desr": "this is description",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         },
                        {"name": "name2",
                         "user": "user2",
                         "src": "github",
                         "url": "www.baidu.com/name/user2",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         }
                        ],
                 page={"start": 4, "end": 11, "cur": 6, "url": ['1', '3', '4', '5']}
                 )
   fp.write(s)
#
tmp = env.get_template("main1.html")
print(tmp.render(repos=[{"name": "name1",
                         "user": "user1",
                         "src": "github",
                         "url": "www.baidu.com/name/user1",
                         "desr": "this is description",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         },
                        {"name": "name2",
                         "user": "user2",
                         "src": "github",
                         "url": "www.baidu.com/name/user2",
                         "license": "GPL3",
                         "star": 334,
                         "fork": 3432,
                         "watch": 324,
                         "lang": "C++"
                         }
                        ],
                 page={"start": 4, "end": 11, "cur": 6, "url": ['1', '3', '4', '5']}
                 ))

def inhightlight(s:str,l:list):
    l1=[]
    for i in l:
        i:str
        t=i.replace("<em>","")
        t=t.replace("</em>","")
        t=t.lower()
        l1.append(t)
    
    for i in l1:
        if s.lower() in i:
            return True
    return False


