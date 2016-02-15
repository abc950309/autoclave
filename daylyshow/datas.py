from daylyshow import db
from daylyshow.config import *

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
            for line in direct_list:
                if line in data:
                    setattr(self, line, data[line])
                else:
                    setattr(self, line, None)
            for line in dbref_list:
                if line in data:
                    setattr(self, '__' + line, data[line])
            for line in multidbref_list:
                if line in data:
                    setattr(self, '__' + line, data[line])
        
        def __getattribute__(self, key):
            "Emulate type_getattro() in Objects/typeobject.c"
            v = object.__getattribute__(self, key)
            if hasattr(v, '__dbref_get__'):
               return v.__dbref_get__(self)
            return v

    for line in direct_list:
        setattr(base_data, line, generate_dbref_get(line))
    for line in dbref_list:
        setattr(base_data, line, generate_multidbref_get(line))
    
    return base_data

def generate_dbref_get(line):
    class get_dbref(object):
        def __dbref_get__(self):
            if not hasattr(self, '__' + line):
                return None
            if not hasattr(self, '_' + line):
                setattr(
                    self,
                    '_' + line,
                    dbref_cell(db.dereference( getattr(self, '__' + line) ))
                )
            return getattr(self, '_' + line)
    return get_dbref

def generate_multidbref_get(line):
    class get_multidbref(object):
        def __dbref_get__(self):
            if not hasattr(self, '__' + line):
                return None
            if not hasattr(self, '_' + line):
                setattr(
                    self,
                    '_' + line,
                    [dbref_cell(db.dereference(x)) for x in getattr(self, '__' + line)]
                )
            return getattr(self, '_' + line)
    return get_multidbref

class dbref_cell(object):
    def __init__(self, data):
        for line in data:
            setattr(self, line, data[line])
