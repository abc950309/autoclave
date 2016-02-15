import tornado.ioloop
import tornado.web
import tornado.autoreload

import os.path
import datetime
import json
import time
import uuid
import re

from bson.dbref import DBRef

from daylyshow.config import *
import daylyshow.image_generator as imgnt
import daylyshow.datas as datas
from daylyshow.password_tools import encrypt_password, verify_password

from daylyshow import db

caches = {
    "counter": 0,
    "sessions": {},
    "users": {},
}

check_email_addr = lambda x: (re.match( r"[^@]+@[^@]+\.[^@]+", x) != None)

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    #uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password.lower()) is None

    # searching for symbols
    #symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or lowercase_error )

    return password_ok

def get_arg_by_list(needed = None, optional = None):
    """目的为获取参数的装饰器
    列表 needed 中为必须参数
    列表 optional 中为可选参数
    """
    def _deco(func):
        def __deco(self, *args, **kwargs):
            arguments = {}
            if needed:
                for line in needed:
                    arguments[line] = self.get_argument(line, None)
                    if not arguments[line] or len(arguments[line]) == 0:
                        raise tornado.web.HTTPError(400)
                        self.finish()
            if optional:
                for line in optional:
                    arguments[line] = self.get_argument('name', None)
                    if len(arguments[line]) == 0:
                        arguments[line] = None
            
            kwargs.update(arguments)
            return func(self, *args, **kwargs)
        return __deco
    return _deco


class User(datas.generate_base_data_class(USER_DATA_CONF)):
    
    global caches
        
    def __init__(self, uid, fresh = False):
        if (uid not in caches['users']) or fresh:
            user = caches['users'][uid] = db["users"].find_one({"_id": uid})
        else:
            user = caches['users'][uid]
        self.build(user)
        
        self.access_time = time.time()

class Session(datas.generate_base_data_class(SESSION_DATA_CONF)):
    
    global caches
        
    def __init__(self, session):
        self.build(session)
        self.access_time = time.time()

clear_users_caches = datas.generate_caches_clear_func('users')
clear_sessions_caches = datas.generate_caches_clear_func('sessions')

class BaseHandler(tornado.web.RequestHandler):
    
    global caches
    
    """
    Base Handler，提供基本服务。
    添加了Session和验证处理。
    """
    
    error_write = lambda self, error_name: (
        self._error_write(error_name) or self.finish()
    )
    
    def initialize(self):
        self.ui['site_title'] = SITE_TITLE
        self.ui['navbar_list'] = NAVBAR_LIST
        self.ui['class_name'] = self.class_name
        self.ui['locals'] = locals
        pass
    
    def new_session(self):
        session_id = str(uuid.uuid4().hex)
        creation = int(time.time())
        db["sessions"].insert(
            {
                "_id": session_id,
                "uid": 0,
                "creation": creation,
                "expired": creation + EXPIRED_TIME,
            }
        )
        self.set_secure_cookie("session_id", session_id, expires = creation + EXPIRED_TIME)
        return session_id

    def fresh_current_user(self):
        self._current_user = self.get_current_user(fresh = True)

    def fresh_session(self):
        session = db["sessions"].find_one({"_id": self.session_id})
        
        if not session:
            self.session_id = self.new_session()
            self.fresh_session()
        else:
            self.session = caches['sessions'][self.session_id] = Session(session)
        
    def change_session(self, list):
        db["sessions"].update_one(
            {"_id": self.session_id},
            {
                "$set": list,
                "$currentDate": {"lastModified": True}
            }
        )
        self.fresh_session()
    
    def fresh_all(self):
        self.fresh_session()
        self.fresh_current_user()
    
    def get_session(self):
        session_id = self.get_secure_cookie("session_id")
        if not session_id:
            self.session_id = self.new_session()
        else:
            self.session_id = session_id.decode()
        
        if self.session_id in caches['sessions']:
            #print("Get From Cache sessions")
            self.session = caches['sessions'][self.session_id]
        else:
            #print("Not Get From Cache sessions")
            self.fresh_session()
    
    def mobile_checker(self):
        if self.request.headers['User-Agent'].find("Mobile") != -1 :
            self.mobile_flag = True
        else:
            self.mobile_flag = False
    
    def ajax_checker(self):
        try:
            self.ajax_flag = self.get_argument('ajax_flag')
        except:
            self.ajax_flag = None
    
    def prepare(self):
    
        self.session_id = None
        self.session = None
        self.render_data = {}
        
        self.get_session()
        self.ajax_checker()
        self.mobile_checker()
        
        self.prepare_c()
        
        if self.get_login_url() not in self.request.uri:
            self.authenticate()
    
    def add_render(self, name, val):
        self.render_data[name] = val
    
    def put_render(self, template_name, **kwargs):
        self.render_data.update(kwargs)
        self.render_data['__keys__'] = self.render_data.keys()
        self.render(template_name, **(self.render_data))
    
    def get_current_user(self, fresh = False):
        if self.session.uid != 0:
            return User(self.session.uid, fresh)
        return None
    
    @tornado.web.authenticated
    def authenticate(self):
        pass
    
    def prepare_c(self):
        pass
    
    def on_finish_c(self):
        pass
    
    def on_finish(self):
        self.on_finish_c()
        
        if hasattr(self, '_current_user') and getattr(self, '_current_user'):
            self.current_user.access_time = time.time()
        self.session.access_time = time.time()
        caches['counter'] += 1
        
        if caches['counter'] >= CACHES_COUNTER_LIMIT:
            clear_users_caches(caches)
            clear_sessions_caches(caches)
    
    @property
    def class_name(self):
        return self.__class__.__name__
    
    def _error_write(self, error_name):
        if self.ajax_flag:
            self.write({
                "status": ERROR_CODES[error_name]['code'],
                "dscp": ERROR_CODES[error_name]['dscp'],
            })
        else:
            self.write({
                "status": ERROR_CODES[error_name]['code'],
                "dscp": ERROR_CODES[error_name]['dscp'],
            })
        self.finish()
    
class LoginAndRegisterHandler(BaseHandler):
    
    def get(self, path = None):
        next = self.get_argument('next', '/')
        if self.current_user:
            self.redirect(next)
        
        self.add_render('custom_js', ['js/login.js'])
        
        self.add_render('next', next)
        self.add_render('title', '注册与登录')
        
        self.put_render("login_and_register.html")
    
    def post(self, path = None):
        if path == "LoginVerif":
            self._post_path_login_verif()
        if path == "Login":
            self._post_path_login()
        if path == "RegisterVerif":
            self._post_path_register_verif()
        if path == "Register":
            self._post_path_register()
        else:
            raise tornado.web.HTTPError(400)
            self.finish()
    
    def _post_path_login_verif(self):
        self.finish()
    
    @get_arg_by_list(["account", "password"])
    def _post_path_login(self, account, password):
        user = db["users"].find_one({"account": account})
        if not user:
            self.error_write("login_no_account")
        if not verify_password(password, user['password']):
            self.error_write("login_wrong_password")
        
        self.change_session({"uid": user["_id"]})
        self.fresh_current_user()
        
        self.write(
            {
                "status": 0,
                "dscp"  : "您已经成功登录了！"
            }
        )
        self.finish()
    
    def _post_path_register_verif(self):
        self.finish()
    
    @get_arg_by_list(["name", "account", "password", "confirm_password"])
    def _post_path_register(self, name, account, password, confirm_password):
        if self.current_user:
            return
        if not check_email_addr(account):
            self.error_write("register_email_format_wrong")
        if not password_check(password):
            self.error_write("register_password_format_wrong")
        if password != confirm_password:
            self.error_write("register_confirm_password_wrong")
        
        same_name_user = db.users.find_one({"account": account})
        if same_name_user:
            self.error_write("register_same_email")
        
        id = str(uuid.uuid4().hex)
        result = db["users"].insert(
            {
                "_id": id,
                "name": name,
                "account": account,
                "password": encrypt_password(password),
            }
        )
        
        if result:
            self.change_session({"uid": id})
            self.fresh_current_user()
            
            self.write(
                {
                    "status": 0,
                    "dscp"  : "您已经完成注册！"
                }
            )
        
        self.finish()


class IndexHandler(BaseHandler):
    def get(self):
        self.add_render('title', '今日图片')
        self.put_render("index.html")


class EditerHandler(BaseHandler):
    def get(self):
        self.add_render('custom_js', ['js/zabuto_calendar.min.js', 'js/editer.js'])
        self.add_render('custom_css', ['css/zabuto_calendar.min.css'])
        
        self.add_render('events', [])
        
        self.add_render('title', '编辑日历')
        self.put_render("editer.html")
