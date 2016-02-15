from autoclave import db
from autoclave.config import *

def generate_caches_clear_func( name ):
    def clear(caches):
        if len(caches[name]) >= CACHES_NUMBER_LIMIT:
            need_to_del_list = sorted(
                caches[name].keys(),
                key = (lambda d : caches[name][d].access_time)
            )[0:(len(caches[name]) - CACHES_NUMBER_LIMIT)]
            for line in need_to_del_list:
                del caches[name][line]
    return clear

def generate_base_data_class( setting ):
    
    """参数为class的设置
    传入dict
    项内容为字符串 'DBRef'，按照DBRef处理。
    项内容为字符串 'MultiDBRef'，按照DBRef的List处理。
    项内容为字符串 'Direct'，按照正常内容处理。
    """
    
    direct_list = []
    dbref_list = []
    multidbref_list = []
    for line in setting:
        if setting[line] == 'DBRef':
            dbref_list.append(line)
        elif setting[line] == 'MultiDBRef':
            multidbref_list.append(line)
        else:
            direct_list.append(line)

    class base_data(object):
        
        def build(self, data):
            self._data = data
            self._dbref_data = {}

        def get_dict(self):
            return self._data

        def get(self, key):
            return self._data[key] if key in self._data else None
        
        def __getitem__(self, key):
            return self.get(key)
        
        def __getattribute__(self, key):
            if key == "_data":
                return object.__getattribute__(self, "_data")
            
            if key in direct_list:
                return self._data[key] if key in self._data else None
            
            if key in dbref_list:
                if key in self._dbref_data:
                    return self._dbref_data[key]
                if key in self._data:
                    self._dbref_data[key] = dbref_cell(db.dereference(self._data[key]))
                    return self._dbref_data[key]
                return None
            
            if key in multidbref_list:
                if key in self._dbref_data:
                    return self._dbref_data[key]
                if key in self._data:
                    self._dbref_data[key] = [dbref_cell(db.dereference(x)) for x in self._data[key]]
                    return self._dbref_data[key]
                return None
            
            v = object.__getattribute__(self, key)
            if hasattr(v, '__get__'):
               return v.__get__(self)
            return v
    return base_data

class dbref_cell(object):
    def __init__(self, data):
        self._data = data
    
    def get_dict(self):
        return self._data
    
    def __getattribute__(self, key):
        try:
            v = object.__getattribute__(self, key)
        except AttributeError as e:
            if key in self._data:
                return self._data[key]
            raise AttributeError(e)
        if hasattr(v, '__get__'):
           return v.__get__(self)
        return v
