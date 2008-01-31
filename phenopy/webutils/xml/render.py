
from phenopy.xml_tools import XML_Dumper
from colubrid import HttpResponse
from phenopy.decorators import generic_decorator
from phenopy.webutils.cookies import Cookies
import os, os.path, sys
import libxml2, time

class settings(object):
    pass

class render(generic_decorator):
    def __call__(self,  cache=False,
                        format=True,
                        debug=False,
                        root_tag="data",
                        content_type='text/xml'):
 
        dumper = XML_Dumper(root_tag)

        time_call = time.time()

        if not hasattr(self.func_self, 'cookies'):
            self.func_self.cookies = Cookies()

        c = self.orig_func(**self.func_kwargs) or {}
        time_call_elapsed = time.time() - time_call

        time_dump = time.time()
        dom =  dumper.to_dom(**c)
        time_dump_elapsed = time.time() - time_dump
        
        results = dom.serialize(format=True)

        if debug:
            print results

        time_proc = time.time()
        
        if debug:
            print "Time profiling. xml dump: %f,  call time %f, total %f"%(time_dump_elapsed,
                                                                           time_call_elapsed,
                                                                           time_dump_elapsed+time_call_elapsed)
        response = HttpResponse(results,[('Content-Type',content_type)])
        self.func_self.cookies.cookize(response)
        return response
