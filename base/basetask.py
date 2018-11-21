#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BaseTask(dict):
    delagation={"name",'is_more'}

    def __init__(self, name,is_more=False):
        super().__init__()
        self['name']=name
        self['is_more']=is_more

    def __getattribute__(self, name):
        delaga=type(self).__dict__['delagation']
        if name in delaga:
            return super().__getitem__(name)
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name in self.delagation:
            super().__setitem__(name,value)
        else:
            return super().__setattr__(name, value)

    def __eq__(self, other):
        if isinstance(other,BaseTask ):
            return other.name == self.name
        if isinstance(other, str):
            return other == self.name
        return False

    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self['name']

