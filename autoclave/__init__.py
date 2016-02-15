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


says_dict = {
    "tilimer": "samuel-cui-says-",
    "samuel": "tilimer-chen-says-",
}
to_says_dict = {
    "tilimer": "tilimer-chen-says-",
    "samuel": "samuel-cui-says-",
}

image_says_dict = {
    "tilimer": "Tilimer Chen Says",
    "samuel": "Samuel Cui Says",
}

settings = {
    "samuel": {
        "template": os.path.join(os.path.dirname(__file__), "image_template", "template_tilimer.bmp"),
        "text_color": (54,60,76,256),
        "date_color": (54,60,76,256),
        "line_color": (220,220,220,256),
        "qmark_color": (200,200,200,256),
        "used_width": 580,
    },
    "tilimer": {
        "text_color": (54,60,76,256),
        "date_color": (54,60,76,256),
        "line_color": (220,220,220,256),
        "qmark_color": (200,200,200,256),
    },
}

class MainHandler(tornado.web.RequestHandler):
    def get(self, name):
        
        date = datetime.datetime.now()
        file_name = says_dict[name] + date.strftime("%Y-%m-%d") + ".png"
        
        if not os.path.isfile(os.path.join(os.path.dirname(__file__), "static", "output", file_name)):
            file_path = "/static/image/nothing.png"
        else:
            file_path = "/static/output/" + file_name
        
        self.render(
            "index.html",
            title = "主页",
            name = name,
            file_path = file_path
        )

class DownloadHandler(tornado.web.RequestHandler):
    def get(self, name):
        date = datetime.datetime.now()
        file_name = says_dict[name] + date.strftime("%Y-%m-%d") + ".png"
        
        self.set_header ('Content-Type', 'application/octet-stream')
        self.set_header ('Content-Disposition', 'attachment; filename=' + file_name)
        
        with open(os.path.join(os.path.dirname(__file__), "static", "output", file_name), 'rb') as f:
            data = f.read()
            self.write(data)
        self.finish()

class EditerHandler(tornado.web.RequestHandler):
    def get(self, name):
        
        raw_list = os.listdir( os.path.join( os.path.dirname(__file__), "static", "output"))
        
        list = []
        for line in raw_list:
            if os.path.isdir( os.path.join( os.path.dirname(__file__), "static", "output", line ) ) or says_dict[name] in line:
                continue
            list.append(line)
        
        signstr = to_says_dict[name] + "%Y-%m-%d.png"
        
        event_data = []
        for line in list:
            date = datetime.datetime.strptime(line, signstr)
            item_dict = {
                "date": date.strftime("%Y-%m-%d"),
                #"badge": True,
            }
            event_data.append(item_dict)
        
        self.render(
            "editer.html",
            title = "主页",
            name = name,
            event_data = json.dumps(event_data),
            to_says = to_says_dict[name],
            says = says_dict[name],
        )

class EditHandler(tornado.web.RequestHandler):
    def post(self, name):
        raw_date = self.get_argument("date")
        text = self.get_argument("text")
        
        if len(text) == 0:
            self.finish()
        date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
        
        image_generator = imgnt.ImageGenerator(setting = settings[name])
        image_generator.generate2save(text = text, says = image_says_dict[name], date = date)
        del image_generator
        
        self.finish()

def start_server(debug = DEBUG, listen_port = LISTEN_PORT):

    application = tornado.web.Application(
        handlers = [
            #(r"/(tilimer|samuel)", MainHandler),
            (r"/", handlers.IndexHandler),
            (r"/LoginAndRegister", handlers.LoginAndRegisterHandler),
            (r"/LoginAndRegister/(\w+)", handlers.LoginAndRegisterHandler),
            #(r"/(tilimer|samuel)/download", DownloadHandler),
            (r"/Editer", handlers.EditerHandler),
            (r"/Setting", handlers.SettingHandler),
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