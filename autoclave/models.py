import os
import os.path
import datetime
import uuid
import time

from autoclave.config import *
import autoclave.image_generator as image_generator
import autoclave.data_container as data_container

from autoclave import db
from autoclave.handlers import caches

class User(data_container.generate_base_data_class(USER_DATA_CONF)):
    
    global caches
    
    @staticmethod
    def get4id(uid, fresh = False):
        if not uid:
            return None
        
        if uid not in caches['users'] or fresh:
            user = db.users.find_one({"_id": uid})
            if not user:
                return None
            caches['users'][uid] = User(user)
        
        return caches['users'][uid]


    def __init__(self, user):
        self.build(user)
        self.access_time = time.time()

class Session(data_container.generate_base_data_class(SESSION_DATA_CONF)):
    
    def __init__(self, session):
        self.build(session)
        self.access_time = time.time()

class Image(data_container.generate_base_data_class(IMAGE_DATA_CONF)):
    
    @staticmethod
    def get4db(data):
        if data:
            return Image(data)
        return None
    
    @staticmethod
    def new(author, layout, date, says, text):
        id = str(uuid.uuid4().hex)
        db.images.insert(
            {
                "_id": id,
                "author": author,
                "says": says,
                "date": date,
                "date_index": date.strftime("%Y-%m-%d"),
                "text": text,
                "layout": layout,
                "path": "/static/output/" + id + ".png",
                "file_path": os.path.join(
                    os.path.dirname(__file__), "static", "output", id + ".png"
                ),
            }
        )
        return Image(db.images.find_one({"_id": id}))
    
    @staticmethod
    def new4layout(layout, date = None, says = "Example Says", text = "为燕权设计的鸡汤高压釜，一个小小的 Web 应用。"):
        if not date:
            date = datetime.datetime(2016, 1, 1, 0, 0, 0)
        
        id = str(uuid.uuid4().hex)
        db.images.insert(
            {
                "_id": id,
                "says": says,
                "date": date,
                "date_index": date.strftime("%Y-%m-%d"),
                "text": text,
                "layout": layout,
                "path": "/static/output/" + id + ".png",
                "file_path": os.path.join(
                    os.path.dirname(__file__), "static", "output", id + ".png"
                ),
            }
        )
        image = Image(db.images.find_one({"_id": id}))
        image.generate()
        return image
    
    def __init__(self, data):
        self.build(data)
    
    def destroy(self):
        os.remove(self.file_path)
        db.images.remove({ "_id": self._id })
    
    def generate(self):        
        image_generator.ImageGenerator(layout = self.layout.get_dict()).generate2save(
            text = self.text,
            says = self.says,
            date = self.date,
            file_path = self.file_path,
        )


class PairCode(data_container.generate_base_data_class(PAIR_CODE_DATA_CONF)):
    def __init__(self, data):
        self.build(data)

    @staticmethod
    def get4db(data):
        if data:
            return PairCode(data)
        return None
    
    @staticmethod
    def new(pair_to):
        while True:
            id = str(uuid.uuid4().hex)
            if not db.pair_codes.find_one({"code": id[0:16].upper()}):
                break
        db.pair_codes.insert(
            {
                "_id": id,
                "code": id[0:16].upper(),
                "pair_to": pair_to,
            }
        )
        return PairCode(db.pair_codes.find_one({"_id": id}))
    
    def destroy(self):
        db.pair_codes.remove({ "_id": self._id })
