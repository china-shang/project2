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


repos=set()
for i in glob.iglob("repo*"):
    with open(i) as f:
        l=load(f.read())
        s={i['name'] + i['author'] for i in l}
        repos.update(s)

        print(f"has={len(repos)}")

print(f"all repos={len(repos)}")

