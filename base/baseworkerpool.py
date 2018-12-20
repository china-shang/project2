from base.baselooper import BaseLooper
from logger import get_logger
from statist import Statist

logger = get_logger(__name__)


class BaseWorkerPool(BaseLooper):
    def __init__(self, statist: Statist = Statist(), max_size=100):
        super().__init__()
        self._statist = statist
        self._max_size = max_size
        self.now = 0
    
    def increase_worker(self, count=1):
        self.now += 1
        logger.info(f"increase worker {count}")
    
    def decrease_worker(self, count=1):
        self.now -= 1
        logger.info(f"decrease worker {count}")
