import time


class Statist(object):
    
    def __init__(self):
        self.all_repo = 0
        self.all_user = 0
        
        self.start_time = time.time()
        self.last_fail_time = 0
        
        self.repos_from_fail = 0
        self.user_from_fail = 0
        self.fail_cnt = 0
        self.max_fail_interval = 0
        self.min_fail_interval = 0
        
        self.req_count = 0
    
    def increase_repos(self, num=1):
        self.all_repo += num
    
    def increase_user(self, num=1):
        self.all_user += num
    
    def increase_req(self, num=1):
        self.req_count += num
    
    def get_avg_speed(self):
        now = time.time()
        cost = now - self.start_time
        result = (self.all_repo / cost, self.all_user / cost, self.req_count / cost)
        return result
    
    def get_recent_speed(self, sleep_during=0):
        if self.last_fail_time == 0:
            return self.get_avg_speed()
        
        now = time.time()
        cost = now - self.last_fail_time - sleep_during
        result = (self.repos_from_fail / cost, self.user_from_fail / cost, self.req_count / cost)
        return result
    
    def get_cost_time(self):
        now = time.time()
        cost = now - self.start_time
        return cost
    
    def record_error(self):
        now = time.time()
        interval = now - self.last_fail_time
        self.max_fail_interval = max(interval, self.max_fail_interval)
        self.min_fail_interval = min(interval, self.min_fail_interval)
        
        self.fail_cnt += 1
        self.last_fail_time = now


def test():
    statist = Statist()
    statist.get_avg_speed()


if __name__ == "__main__":
    test()
