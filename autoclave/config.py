import os.path

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
    {"class_name": "SettingHandler", "path": "/Setting", "dscp": "设置"},
]

USER_DATA_CONF = {
    "_id" : "Direct",
    "password" : "Direct",
    "account" : "Direct",
    "pair" : "DBRef",
    "name" : "Direct",
    "lastModified" : "Direct",
    "says" : "Direct",
    "layout" : "DBRef",
    "confirmed": "Direct",
    "email_confirmed": "Direct",
}

SESSION_DATA_CONF = {
    "_id": "Direct",
    "uid": "Direct",
    "creation": "Direct",
    "expired": "Direct",
    "lastModified" : "Direct",
}

IMAGE_DATA_CONF = {
    "_id": "Direct",
    "author": "DBRef",
    "file_path": "Direct",
    "path": "Direct",
    "says": "Direct",
    "date": "Direct",
    "date_index": "Direct",
    "text": "Direct",
    "layout": "DBRef",
    "lastModified" : "Direct",
}

PAIR_CODE_DATA_CONF = {
    "_id": "Direct",
    "code": "Direct",
    "pair_to": "DBRef",
    "lastModified" : "Direct",
}

EMAIL_CODE_EXPIRED_TIME = 7 * 24 * 3600
EMAIL_CODE_DATA_CONF = {
    "_id": "Direct",
    "code": "Direct",
    "user": "DBRef",
    "expired": "Direct",
    "lastModified" : "Direct",
}

ERROR_CODES = {
    "register_needed_arg_missing": {"code": 1000, "dscp": "请您输入有效的姓名。"},
    "register_email_format_wrong": {"code": 1001, "dscp": "请您输入有效的 E-Mail。"},
    "register_password_format_wrong": {"code": 1002, "dscp": "请您输入有效的密码，需要至少8位、包含字母和数字的密码。"},
    "register_confirm_password_wrong": {"code": 1003, "dscp": "您输入的确认密码与密码不匹配。"},
    "register_same_email": {"code": 1004, "dscp": "您输入的 E-Mail 已经被注册。"},
    
    "login_no_account": {"code": 1100, "dscp": "您输入的账号不存在。"},
    "login_wrong_password": {"code": 1101, "dscp": "您输入的密码是错误的。"},
    
    "generate_unconfirmed": {"code": 1200, "dscp": "您还没有进行有效设置，无法生成图片。<a href=\"/Setting\">点击这里</a>进行设置。"},
    
    "setting_arg_missing": {"code": 1500, "dscp": "请您输入有效的设置。"},
    "setting_confirm_password_wrong": {"code": 1501, "dscp": "您输入的确认密码与密码不匹配。"},
    "setting_password_format_wrong": {"code": 1502, "dscp": "请您输入有效的密码，需要至少8位、包含字母和数字的密码。"},
    "setting_no_layout": {"code": 1503, "dscp": "您请求的布局不存在。"},
    "setting_double_pair": {"code": 1504, "dscp": "您已经进行了配对。"},
    "setting_bad_pair": {"code": 1505, "dscp": "您输入的配对代码不正确。"},
}
