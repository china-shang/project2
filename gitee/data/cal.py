#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import glob


def load(s) -> list:
    l=[]
    try:
        l=json.loads(s)
    except json.JSONDecodeError as e:
        #print(e.pos)
        l.extend(load(s[:e.pos]))
        l.extend(load(s[e.pos:]))
    return l


n=0
repos=set()
for i in glob.iglob("repo*"):
    with open(i) as f:
        l=load(f.read())
        n  += len(l)
        s={i['name'] + i['author'] for i in l}
        repos.update(s)

        print(f"has={len(repos)}")
        print(f"about has={n}")

print(f"all repos={len(repos)}")
print(f"about all repos={n}")

