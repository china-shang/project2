class RateLimit(object):
    req_rate_limit = 1
    
    @classmethod
    def get_req_rate_limit(cls):
        return cls.req_rate_limit
