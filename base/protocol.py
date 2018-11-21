# [B]     [L]      [I]      [?]
# [from:1][index:4][which:2][status:1][data:?][eof]
# [header:1+4+2+1=8

class Protocol(object):
    Success = True
    Fail = False
    
    Request = 0
    Response = 1
    
    TaskDispatch = 1
    Control = 0
    
    Key_command = "command"
    Key_repos_buf_count = "repos_buf_count"
    Key_user_buf_count = "repos_buf_count"
    Key_get_repos_buf = "get_repos_buf"
    Key_get_user_buf = "get_user_buf"
    Key_put_buf = "put_buf"
    Key_complete_buf = "complete_buf"
    Key_fail_buf = "fail_buf"
    
    Value_start = "start"
    Value_get_status = "status"
    
    def __init__(self):
        pass
