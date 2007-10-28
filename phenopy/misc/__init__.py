import new,re
from datetime import datetime, date

import inspect

def any_class(name):
    o = new.classobj(name, (object,), {'__init__':lambda self,**kw: self.__dict__.update(kw)})
    module = inspect.getmodule(o)
    if not getattr(module, o.__name__, None):
        setattr(module, o.__name__, o)
    return getattr(module, o.__name__)

def datetime_from_iso_str(s):
    return datetime(*tuple([int(x) for x in re.split(r'\D', s)]))

def date_from_iso_str(s):
    return date(*tuple([int(x) for x in re.split(r'\D', s)]))

def attr_exists(o, a):
    return hasattr(o, a) and getattr(o, a)


def guard(object):
    def __enter__(o):
        self.o = o

    def __exit__(o):
        del self.o

    
