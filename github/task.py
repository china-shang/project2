import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__name__), "../base"))

from base.basetask import BaseTask


class Task(BaseTask):
    delagation = BaseTask.delagation ^ {"is_org"}
    
    def __init__(self, name, is_org=False, more=False):
        super().__init__(name, more)
        self['is_org'] = is_org
    
    def to_tuple(self):
        return (self['name'], self['is_org'])
