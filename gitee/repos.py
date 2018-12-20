from base.baserepos import BaseRepos


class Repos(BaseRepos):
    delagation = BaseRepos.delagation ^ {'nickname','url', 'author',
                                         'lang', 'viplevel',
                                         'desc', 'updatetime',
                                         'watch', 'star',
                                         'fork', 'isfork', 'forkfrom'}
    
    def __init__(self, name, nickname, author,
                 lang, viplevel, desc, updatetime,
                 watch, star, fork,url,
                 isfork=False, forkfrom=None):
        super().__init__(name)
        self['nickname'] = nickname
        self['author'] = author
        self['url'] = url
        self['lang'] = lang
        self['viplevel'] = viplevel
        self['desc'] = desc
        self['updatetime'] = updatetime
        self['watch'] = watch
        self['star'] = star
        self['fork'] = fork
        self['isfork'] = isfork
        self['forkfrom'] = forkfrom
    
    def __hash__(self):
        return hash(self['author'] + self['name'])
    
    def __eq__(self, other):
        if isinstance(other, Repos):
            return self['author'] == other['author'] \
                   and self['name'] == self['name']


if __name__ == '__main__':
    r = Repos.delagation
    print(r)
