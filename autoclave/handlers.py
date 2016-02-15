import tornado.ioloop
import tornado.web
import tornado.autoreload

import os
import os.path
import datetime
import json
import time
import uuid
import re

from bson.dbref import DBRef

caches = {
    "counter": 0,
    "sessions": {},
    "users": {},
}

from autoclave.config import *
import autoclave.image_generator as image_generator
import autoclave.data_container as data_container
import autoclave.models as models
from autoclave.password_tools import encrypt_password, verify_password

from autoclave import db

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
                    arguments[line] = self.get_argument(line, None)
                    if arguments[line] and len(arguments[line]) == 0:
                        arguments[line] = None
            
            kwargs.update(arguments)
            return func(self, *args, **kwargs)
        return __deco
    return _deco


clear_users_caches = data_container.generate_caches_clear_func('users')
clear_sessions_caches = data_container.generate_caches_clear_func('sessions')

new_pair_code = lambda x : models.PairCode.new(DBRef("users", x))

def get_error_string(error_name):
    return ERROR_CODES[error_name]['dscp']

class BaseHandler(tornado.web.RequestHandler):
    
    global caches
    
    """
    Base Handler，提供基本服务。
    添加了Session和验证处理。
    """
    
    error_write = lambda self, error_name: (
        self._error_write(error_name) or self.finish()
    )


    @property
    def class_name(self):
        return self.__class__.__name__


    _template_namespace = {
        'site_title': SITE_TITLE,
        'navbar_list': NAVBAR_LIST,
        'get_error_string': get_error_string,
        'dereference': db.dereference,
    }
    
    
    def initialize(self):
        self.ui.update(self._template_namespace)
        self.ui['class_name'] = self.class_name


    def new_session(self):
        session_id = str(uuid.uuid4().hex)
        creation = int(time.time())
        db.sessions.insert(
            {
                "_id": session_id,
                "uid": 0,
                "creation": creation,
                "expired": creation + EXPIRED_TIME,
            }
        )
        self.set_secure_cookie("session_id", session_id, expires = creation + EXPIRED_TIME)
        return session_id


    def fresh_current_user(self, uid = None):
        if uid and uid != 0:
            models.User.get4id(uid, fresh = True)
        else:
            self._current_user = self.get_current_user(fresh = True)


    def fresh_session(self):
        session = db.sessions.find_one({"_id": self.session_id})
        
        if not session:
            self.session_id = self.new_session()
            self.fresh_session()
        else:
            self.session = caches['sessions'][self.session_id] = models.Session(session)


    def change_session(self, list):
        db.sessions.update_one(
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
        return models.User.get4id(self.session.uid, fresh)


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
        if hasattr(self, 'session') and getattr(self, 'session'):
            self.session.access_time = time.time()
        caches['counter'] += 1
        
        if caches['counter'] >= CACHES_COUNTER_LIMIT:
            clear_users_caches(caches)
            clear_sessions_caches(caches)


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


class LoginAndRegisterHandler(BaseHandler):
    
    def get(self, path = None):
        if path == "Logout":
            self._get_path_logout()
            return
        next = self.get_argument('next', '/')
        if self.current_user:
            self.redirect(next)
        
        self.add_render('custom_js', ['js/login.js'])
        
        self.add_render('next', next)
        self.add_render('title', '注册与登录')
        
        self.put_render("login_and_register.html")
    
    def post(self, path = None):
        self.path = path
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
    
    def _get_path_logout(self):
        self.change_session({"uid": 0})
        self.fresh_current_user()
        self.redirect(self.get_login_url())
    
    def _post_path_login_verif(self):
        self.finish()
    
    @get_arg_by_list(["account", "password"])
    def _post_path_login(self, account, password):
        if self.current_user:
            return
        user = db.users.find_one({"account": account})
        if not user:
            self.error_write("login_no_account")
            return
        if not verify_password(password, user['password']):
            self.error_write("login_wrong_password")
            return
        
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
            return
        if not password_check(password):
            self.error_write("register_password_format_wrong")
            return
        if password != confirm_password:
            self.error_write("register_confirm_password_wrong")
            return
        
        same_name_user = db.users.find_one({"account": account})
        if same_name_user:
            self.error_write("register_same_email")
            return
        
        id = str(uuid.uuid4().hex)
        result = db.users.insert({
            "_id": id,
            "name": name,
            "account": account,
            "password": encrypt_password(password),
        })
        
        if result:
            self.change_session({"uid": id})
            self.fresh_current_user()
            
            self.write({
                "status": 0,
                "dscp"  : "您已经完成注册！"
            })
        
        self.finish()

    def on_finish_c(self):
        if hasattr(self, "path") and self.path == "Register":
            new_pair_code(self.current_user._id)

class IndexHandler(BaseHandler):
    def get(self):
        
        path = "/static/image/nothing.png"
        if self.current_user.pair:
            image = models.Image.get4db(db.images.find_one({
                "author": self.current_user["pair"],
                "date_index": datetime.datetime.now().strftime("%Y-%m-%d"),
            }))
            if image:
                path = image.path
        else:
            image = models.Image.get4db(db.images.find_one({
                "author": DBRef("users", self.current_user._id),
                "date_index": datetime.datetime.now().strftime("%Y-%m-%d"),
            }))
            if image:
                path = image.path
        self.add_render('path', path)
        
        self.add_render('title', '今日图片')
        self.put_render("index.html")


class EditerHandler(BaseHandler):
    def get(self):
        self.add_render('custom_js', ['js/zabuto_calendar.js', 'js/editer.js'])
        self.add_render('custom_css', ['css/zabuto_calendar.min.css'])
        self.xsrf_token
        
        images = db.images.find({
            "author": DBRef("users", self.current_user._id),
        })
        events = []
        for event in images:
            events.append({
                "date": event["date_index"],
                "values": {
                    "path": event["path"],
                    "text": event["text"],
                },
            })
        
        self.add_render('events', events)
        
        self.add_render('title', '编辑日历')
        self.put_render("editer.html")


    @get_arg_by_list(["text", "date"])
    def post(self, text, date):
        if not self.current_user.confirmed:
            self.error_write("generate_unconfirmed")
            return
        
        dealed_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        image = models.Image.get4db(db.images.find_one({
            "author": DBRef("users", self.current_user._id),
            "date_index": dealed_date.strftime("%Y-%m-%d"),
        }))
        if image:
            image.destroy()
        
        self.image = models.Image.new(
            author = DBRef("users", self.current_user._id),
            layout = self.current_user["layout"],
            date = dealed_date,
            says = self.current_user.says,
            text = text,
        )
        self.write({
            "date": self.image.date_index,
            "values": {
                "path": self.image.path,
                "text": text,
            },
            "status": 0,
        })


    def on_finish_c(self):
        if hasattr(self, "image"):
            self.image.generate()


class SettingHandler(BaseHandler):
    
    def get(self):
        self.add_render('custom_js', ['js/setting.js'])
        
        self.add_render(
            'pair_code',
            models.PairCode.get4db(
                db.pair_codes.find_one({ "pair_to": DBRef("users", self.current_user._id) })
            )
        )
        self.add_render('layout_options', db.layouts.find({}, {"_id": True, "name": True, "display": True}).sort("name"))
        self.add_render('title', '设置')
        self.put_render("setting.html")
    
    @get_arg_by_list(optional = ["password", "confirm_password", "layout", "says", "pair_code"])
    def post(self, password, confirm_password, layout, says, pair_code):
        for line in [password, layout, says]:
            if line:
                break
        else:
            self.error_write("setting_arg_missing")
            return
        
        self.set_dict = {}
        
        if password:
            if password != confirm_password:
                self.error_write("setting_confirm_password_wrong")
                return
            if not password_check(password):
                self.error_write("setting_password_format_wrong")
                return
            self.set_dict["password"] = encrypt_password(password)
        
        if layout and (not self.current_user.layout or layout != self.current_user.layout._id):
            if not db.layouts.find_one({"_id": layout}):
                self.error_write("setting_no_layout")
                return
            self.set_dict["layout"] = DBRef("layouts", layout)
        
        if says and (not self.current_user.says or says != self.current_user.says):
            self.set_dict["says"] = says
        
        if pair_code:
            if self.current_user.pair:
                self.error_write("setting_double_pair")
                return
            self.dealed_pair_code = models.PairCode.get4db(db.pair_codes.find_one({ "code": pair_code }))
            if not self.dealed_pair_code:
                self.error_write("setting_bad_pair")
                return
            self.set_dict["pair"] = self.dealed_pair_code["pair_to"]
        
        if len(self.set_dict) == 0:
            self.error_write("setting_arg_missing")
            return
        
        self.result = db.users.update_one(
            {"_id":self.current_user._id},
            {
                "$set": self.set_dict,
                "$currentDate": {"lastModified": True}
            }
        )
        self.fresh_current_user()
        
        if self.ajax_flag:
            self.write({
                "status": 0,
            })
        else:
            self.redirect(self.request.uri)
    
    def delete(self, path = None):
        if path == "Pair":
            self._delete_path_pair()
        else:
            raise tornado.web.HTTPError(400)
    
    def _delete_path_pair(self):
        users_list = [ self.current_user._id, self.current_user.pair._id ]
        db.users.update_many(
            {"_id": { "$in": users_list }},
            {
                "$unset": {"pair": True},
                "$currentDate": {"lastModified": True},
            }
        )
        
        for line in users_list:
            new_pair_code(line)
        self.fresh_current_user()
        self.fresh_current_user(users_list[1])
        
        if self.ajax_flag:
            self.write({
                "status": 0,
            })
        else:
            self.redirect("/Setting")
        
    def on_finish_c(self):
        if hasattr(self, "result") and self.result:
            if 'password' in self.set_dict:
                self.change_session({"uid": 0})
                self.fresh_current_user()
            
            if hasattr(self, "dealed_pair_code"):
                db.users.update_one(
                    {"_id": self.dealed_pair_code.pair_to._id},
                    {
                        "$set": {"pair": DBRef("users", self.current_user._id)},
                        "$currentDate": {"lastModified": True}
                    }
                )
                self.dealed_pair_code.destroy()
                self.fresh_current_user(self.dealed_pair_code.pair_to._id)
            
            if not self.current_user.confirmed and self.current_user.layout and self.current_user.says:
                result = db.users.update_one(
                    {"_id":self.current_user._id},
                    {
                        "$set": {"confirmed": True},
                        "$currentDate": {"lastModified": True}
                    }
                )
                self.fresh_current_user()
