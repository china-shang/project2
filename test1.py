#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys


def test():
    print(f"./ is {os.path.realpath(__file__)}")
    print(sys.path)

if __name__  ==  "__main__":
    test()
