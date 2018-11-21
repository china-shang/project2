
from statist import Statist
from base.baselooper import BaseLooper
from base.baseworker import BaseWorker

class BaseWorkPool(BaseLooper):
    def __init__(self,statist:Statist=Statist(),max_size=100):
        super().__init__()
        self._statist=statist
        self._max_size=max_size
    
    def increase_worker(self,count=1):
        pass
    
    def decrease_worker(self,count=1):
        pass
    
    
    
