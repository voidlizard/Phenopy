import inspect, new, itertools, sys

class generic_decorator(object):
    def __init__(self):#, orig_self, *args, **kwargs):
        pass
        
    def get_origrun(self, args=None, kwargs=None):
        if args == None:
            args = self.func_args
        if kwargs == None:
            kwargs = self.func_kwargs

        #return decorated function object
        return lambda:self.orig_func(self.func_self, *args, **kwargs)

    #setter for decorated function object attr
    def set_function_attr(self, name, val):
        setattr(self.orig_func, name, val)

    def __new__(typ, *attr_args, **attr_kwargs):  # argument values of decorator

        def decorator(orig_func): # original function name
            self = object.__new__(typ)
            self.orig_func = orig_func
            self.__init__()

            attr_args
            attr_kwargs
           
            args, varargs, varkw, defaults = inspect.getargspec(orig_func)
            parameters = inspect.formatargspec(args, varargs, varkw, defaults)[1:-1]
    
            wrapper_func_str = """
def %s(%s):
    args, varargs, varkw, defaults = inspect.getargspec(%s)
    kw_args = dict.fromkeys(args)
    f_vals = []
    for key in args:
        kw_args[key] = locals()[key]
        f_vals.append(locals()[key])
    orig_self = f_vals[0]
    caller.func_self   = orig_self
    caller.func_args   = []
    caller.func_kwargs = kw_args
    return caller.__call__(*attr_args, **attr_kwargs)
"""%(orig_func.__name__, parameters, orig_func.__name__)

            exec_dict = locals()
            exec_dict.update(globals())
            exec_dict[orig_func.__name__] = orig_func
            exec_dict['orig_func'] = orig_func
            exec_dict['caller'] = self
            exec_dict['attr_args'] = attr_args        
            exec_dict['attr_kwargs'] = attr_kwargs     

            exec wrapper_func_str in exec_dict
            wrapper_func = locals()[orig_func.__name__]
            wrapper_func.__doc__ = orig_func.__doc__
            wrapper_func.__dict__ = orig_func.__dict__.copy()
            return wrapper_func
                                                        
        return decorator

