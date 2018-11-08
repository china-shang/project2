import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../"))
sys.path.insert(0,os.path.join(os.path.dirname(__name__),"../base"))

from base.basetaskprovider import BaseTaskProvider

class BaseTaskProviderProxy(BaseTaskProvider):
    pass