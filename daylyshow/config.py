SITE_TITLE = "为燕权设计的鸡汤高压釜"

EXPIRED_TIME = 30 * 24 * 60 * 60
COOKIE_SECRET = "PaWCfl8/RriuXAHSL2f7tebQY+uIIEMWnnHXJiiHuJ8="
DEBUG = False
LISTEN_PORT = 8999

CACHES_COUNTER_LIMIT = 1000
CACHES_NUMBER_LIMIT  = 10000

NAVBAR_LIST = [
    {"class_name": "IndexHandler", "path": "/", "dscp": "首页"},
    {"class_name": "EditerHandler", "path": "/Editer", "dscp": "编辑"},
]

USER_DATA_CONF = {
    "_id" : "Direct",
    "password" : "Direct",
    "account" : "Direct",
    "pair" : "DBRef",
    "name" : "Direct",
    "lastModified" : "Direct",
    "says" : "Direct",
    "setting" : "DBRef",
    "confirmed": "Direct",
}

SESSION_DATA_CONF = {
    "_id": "Direct",
    "uid": "Direct",
    "creation": "Direct",
    "expired": "Direct",
    "lastModified" : "Direct",
}

ERROR_CODES = {
    "register_needed_arg_missing": {"code": 1000, "dscp": "请您输入有效的姓名"},
    "register_email_format_wrong": {"code": 1001, "dscp": "请您输入有效的 E-Mail"},
    "register_password_format_wrong": {"code": 1002, "dscp": "请您输入有效的密码，需要至少8位、包含字母和数字的密码"},
    "register_confirm_password_wrong": {"code": 1003, "dscp": "您输入的确认密码与密码不匹配"},
    "register_same_email": {"code": 1004, "dscp": "您输入的 E-Mail 已经被注册"},
    
    "login_no_account": {"code": 1100, "dscp": "您输入的账号不存在"},
    "login_wrong_password": {"code": 1101, "dscp": "您输入的密码是错误的"},
}