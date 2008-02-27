import re, new, exceptions
from phenopy.decorators import generic_decorator
from phenopy.misc import datetime_from_iso_str, date_from_iso_str


class validation_error(Exception):
    pass

class pass_if_empty(generic_decorator):
    def __call__(self, attr='v'):
        if not self.func_kwargs[attr] or self.func_kwargs[attr] == '':
            return
        return self.orig_func(**self.func_kwargs)

class pass_val_if_empty(generic_decorator):
    def __call__(self, attr='v'):
        if not self.func_kwargs[attr] or self.func_kwargs[attr] == '':
            return self.func_kwargs[attr]
        return self.orig_func(**self.func_kwargs)

class with_error(type):
    def __new__(cls, name, bases, dict):
        dict["error"] = new.classobj('%s__error'%name,(validation_error,),{'__init__':lambda s, **kw:s.__dict__.update(kw)})
        who =  type.__new__(cls,name,bases,dict)
        return who

class validator(object):
    __metaclass__ = with_error

    def is_transform(self):
        return False

    def transform(self, v):
        raise exceptions.NotImplementedError()

class and_container(validator):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __call__(self, value):
        self.first(value)
        self.second(value)

    def __and__(self, other):
        return and_container(self, other)

    def is_transform(self):
        return self.first.is_transform() or self.second.is_transform()

    def transform(self, v):
        val = v
        if self.first.is_transform():
            val = self.first.transform(val)
        if self.second.is_transform():
            val = self.second.transform(val) 
        return val
        
class condition(validator):

    def __repr__(self):
        return str(self.__dict__)

    def __and__(self, other):
        return and_container(self, other)

def num(a):
    try:
        return  int(a)
    except:
        try:
            return float(a)
        except:
            pass
    return a
    

class less(condition):

    def __init__(self, what):
        self.what = what
    
    @pass_if_empty('value')
    def __call__(self, value):
        if not (num(value) <= self.what):
            raise self.error(value=self.what)

class more(condition):

    def __init__(self, what):
        self.what = what
    
    @pass_if_empty('value')
    def __call__(self, value):
        if not (num(value) >= self.what):
            raise self.error(value=self.what)

class between(condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @pass_if_empty('value')
    def __call__(self, value):
        if not ( num(value) >= self.a and num(value) <= self.b):
            raise self.error(lo=self.a, hi=self.b)

class is_int(condition):
    @pass_if_empty()
    def __call__(self, v):
        try:
            int(v)
        except:
            raise self.error()

    def is_transform(self):
        return True

    @pass_val_if_empty()
    def transform(self,v):
        return int(v)


class is_float(condition):
    @pass_if_empty()
    def __call__(self, v):
        try:
            float(v)
        except:
            raise self.error()

    def is_transform(self):
        return True

    @pass_val_if_empty()
    def transform(self,v):
        return float(v)

class trunc(condition):

    def __init__(self, len):
        self.len = len

    @pass_if_empty()
    def __call__(self, v):
        try:
            return v[:self.len]
        except:
            raise self.error()

    def is_transform(self):
        return True

    @pass_val_if_empty()
    def transform(self,v):
        return v[:self.len]

class whatever(condition):

    def __init__(self, default=None):
        self.default = default

    def __call__(self, v):
        pass

    def is_transform(self):
        return True

    def transform(self,v):
        if not v:
            return self.default
        return v

class not_empty(condition):
    def __call__(self, v):
        if not ("" != v and None != v):
            raise self.error()

class is_empty(condition):
    def __call__(self, v):
        if "" != v and None != v:
	    raise self.error()

class not_space(condition):
    @pass_if_empty()
    def __call__(self, v):
        if not ("" != v.strip()):
            raise self.error()

class is_like(condition):

    def __init__(self, rstr):
        self.rstr = rstr
        self.re = re.compile(rstr)

    @pass_if_empty('value')
    def __call__(self, value):
        try:
            if not self.re.match(value):
                raise self.error()
        except:
                raise self.error()

class is_datetime(condition):
    @pass_if_empty('v')
    def __call__(self, v):
        try:
            d = datetime_from_iso_str(v)
        except:
            raise self.error()

    def is_transform(self):
        return True

    @pass_val_if_empty()
    def transform(self,v):
        return datetime_from_iso_str(v)

class is_date(condition):
    @pass_if_empty('v')
    def __call__(self, v):
        try:
            d = datetime_from_iso_str(v)
        except:
            raise self.error()

    def is_transform(self):
        return True

    @pass_val_if_empty()
    def transform(self,v):
        return date_from_iso_str(v)


class is_in(condition):
    def __init__(self, *p):
        self.values = set(p)

    @pass_if_empty()
    def __call__(self,v):
        if not (v in self.values):
            raise self.error()
        
class not_(condition):
    def __init__(self, cond):
        self.cond = cond

    def __call__(self, value):
        try:
            self.cond(value)
        except:
            return
        raise self.error()

class is_email(is_like):
    def __init__(self):
        self.re = re.compile(r'.+@.+')
        self.rstr = ":email:"

class has_len(condition):
    def __init__(self, max=None, min=None):
        self.max = max
        self.min = min

    @pass_if_empty('value')
    def __call__(self, value):
        sz = len(value)
        if self.max and sz > self.max:
            raise self.error(min=self.min, max=self.max)
        if self.min and sz < self.min:
            raise self.error(min=self.min, max=self.max)

def validate_dict(scheme, data, disable_transform=False):
    errors = {}
    transform = {}
    for k,v in scheme.__dict__.items():
        if isinstance(v, validator):
            if v.is_transform():
                transform[k] = v #last tranform
            try:
                if not data.has_key(k):
                    data[k] = None
                v(data[k])
            except validation_error, e:
                errors[k] = e
    if not disable_transform and not len(errors):
        for k,v in scheme.__dict__.items():
            try:
                p = data[k]
                data[k] = transform[k].transform(p)
            except KeyError:
                pass
    return errors

#FIXME: colubrid-specific!
class validate_form(generic_decorator):
    def __call__(self, scheme, disable_transform=False):
        self.func_self.form_errors = None
        self.func_self.form_errors = validate_dict(scheme, self.func_self.request.form, disable_transform)
        return self.orig_func(**self.func_kwargs)

