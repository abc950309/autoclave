import tornado.ioloop
import tornado.web
import tornado.autoreload

import os.path
import datetime
import json

from pymongo import MongoClient
from bson.dbref import DBRef

db = MongoClient().autoclave

from autoclave.config import *
import autoclave.image_generator as imgnt
import autoclave.handlers as handlers
import autoclave.datas_sync as datas_sync


def start_server(debug = DEBUG, listen_port = LISTEN_PORT):

    application = tornado.web.Application(
        handlers = [
            (r"/", handlers.IndexHandler),
            (r"/LoginAndRegister", handlers.LoginAndRegisterHandler),
            (r"/LoginAndRegister/(\w+)", handlers.LoginAndRegisterHandler),
            (r"/LoginAndRegister/(EmailConfirm)/([0-9A-F]+)", handlers.LoginAndRegisterHandler),
            (r"/Editer", handlers.EditerHandler),
            (r"/Setting", handlers.SettingHandler),
            (r"/Setting/(\w+)", handlers.SettingHandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        debug = debug,
        cookie_secret = COOKIE_SECRET,
        login_url = "/LoginAndRegister",
        xsrf_cookies= True
    )
    
    application.listen( listen_port )
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    start_server()