class BaseRepos(dict):
    delagation={"name"}

    def __init__(self, name):
        super().__init__()
        self['name']=name
        self.is_more=False

    def __getattribute__(self, name):
        delagation=type(self).__dict__['delagation']
        if name in delagation:
            return super().__getitem__(name)
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        delagation=type(self).__dict__['delagation']
        if name in delagation:
            super().__setitem__(name,value)
        else:
            return super().__setattr__(name, value)

    def __eq__(self, other):
        if isinstance(other,BaseRepos ):
            return other.name == self.name
        if isinstance(other, str):
            return other == self.name
        return False

    def __hash__(self):
        return hash(self.name)

        
    
    
        