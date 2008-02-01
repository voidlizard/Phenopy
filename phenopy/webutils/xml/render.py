
from phenopy.xml_tools import XML_Dumper
from colubrid import HttpResponse
from phenopy.decorators import generic_decorator
from phenopy.webutils.cookies import Cookies
import os, os.path, sys
import libxml2, time, datetime

class settings(object):
    pass

class render(generic_decorator):
    def __call__(self,  cache=False,
                        format=True,
                        debug=False,
                        root_tag="data",
                        content_type='text/xml'):

        def date_time_hook(obj, node):
            fields = ('year', 'month', 'day', 'hour', 'minute', 'second')
            node.newProp('type', 'datetime')
            for x in fields:
                if hasattr(obj, x):
                    node.newProp(x, str(getattr(obj, x)))
        
        hooks = {
            datetime.datetime.__name__ : date_time_hook,
            datetime.date.__name__     : date_time_hook,
            datetime.time.__name__     : date_time_hook,
        }

        dumper = XML_Dumper(root_tag, type_hooks=hooks)

        time_call = time.time()

        if not hasattr(self.func_self, 'cookies'):
            self.func_self.cookies = Cookies()

        c = self.orig_func(**self.func_kwargs) or {}
        time_call_elapsed = time.time() - time_call

        time_dump = time.time()
        dom =  dumper.to_dom(**c)
        time_dump_elapsed = time.time() - time_dump
        
        results = dom.serialize(format=True)

        if debug or settings.debug:
            print results

        time_proc = time.time()
        
        if debug or settings.debug:
            print "Time profiling. xml dump: %f,  call time %f, total %f"%(time_dump_elapsed,
                                                                           time_call_elapsed,
                                                                           time_dump_elapsed+time_call_elapsed)
        response = HttpResponse(results,[('Content-Type',content_type)])
        self.func_self.cookies.cookize(response)
        return response
