import inspect, re

def before_after_aspects(f, name=None, before=None, after=None):
    if name is None:
        name = f.func_name
    def wrapped(*args, **kwargs):
        if before:
            before(*args, **kwargs)
        result = f(*args, **kwargs)
        if after:
            after(*args, **kwargs)
        return result
    wrapped.__doc__ = f.__doc__
    return wrapped

class Before_After_Call(type):
    def __new__(cls,classname,bases,classdict):
        skip = re.compile(r'^_.+')
        before = None
        after = None

        if classdict.has_key('__call_before__'):
            before = classdict["__call_before__"]

        if classdict.has_key('__call_after__'):
            after = classdict["__call_after__"]

        for name, value in classdict.items():

            if skip.match(name):
                continue

            if inspect.isroutine(value):
                classdict[name] = before_after_aspects(value, None, before, after)

        who =  type.__new__(cls,classname,bases,classdict)
        return who
