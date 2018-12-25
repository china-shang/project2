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
        s={i['url'][19:]  for i in l}
        n += len(l)
        repos.update(s)

        print(f"about has={n}")
        print(f"has={len(repos)}")

print(f"all repos={len(repos)}")
print(f"about has {n}")

