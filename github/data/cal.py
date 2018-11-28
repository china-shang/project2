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
for i in glob.iglob("repo*"):
    with open(i) as f:
        l=load(f.read())
        print(f"l={len(l)}")
        n += len(l)

print(f"all repos={n}")

