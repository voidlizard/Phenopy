#from xml_tools import XML_Dumper
from phenopy.xml_tools.dumper2 import XML_Dumper
from phenopy.xml_tools import Xslt
from phenopy.misc import any_class
from colubrid import HttpResponse
from colubrid.exceptions import HttpFound
from phenopy.decorators import generic_decorator
from phenopy.webutils.cookies import Cookies
import os, os.path, sys, datetime
import libxslt, libxml2, time, re

class settings(object):
    searchpath = ''
    charset='utf-8'
    debug = False
    dom_postprocessor = None
    cache = True
    cut_xml_header = False

xslt_cache = {}

class render(generic_decorator):

    def _postprocess_dom(self, dom):

        klz = self.func_self.__class__
        if hasattr(klz, 'XSLT_RENDER_HINTS'):
            hints_class = getattr(klz, 'XSLT_RENDER_HINTS')
            hints = hints_class()
            return hints.dom_postprocess(dom, self.func_self)

        return dom

    def __call__(self,  template=None,
                        format=True,
                        root_tag="data",
                        content_type='text/html',
                        raw=False,
                        cut_xml_header=False):

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

        time_start = time.time()
        # START, begin pre-call operations

        dumper = XML_Dumper(root_tag=root_tag, type_hooks=hooks)

        time_call = time.time()
        # CALL, get some data

        if not hasattr(self.func_self, 'cookies'):
            self.func_self.cookies = Cookies()

        c = self.orig_func(**self.func_kwargs) or {}

        time_proc = 0
        results = None
        time_dump = 0
        a_point = 0

        if template and not raw:
            time_dump = time.time()
            # DUMP, begin dumping dom

            dom =  dumper.to_dom(**c)

            if settings.debug:
                print dom.serialize(format=True, encoding=settings.charset)

            path = settings.searchpath
            path = os.path.abspath(os.path.join(path, template))

            xslt = None
            if settings.cache:
                try:
                    xslt = xslt_cache[path]
                except KeyError:
                    xslt = Xslt(path)
                    xslt_cache[path] = xslt
            else:
                xslt = Xslt(path)

            time_proc = time.time()
            # PROC, begin processing xml

            result_dom = xslt.apply_to_doc(dom)
            result_dom = self._postprocess_dom(result_dom)
            results = result_dom.serialize(format=format, encoding=settings.charset)


            if cut_xml_header or settings.cut_xml_header:
                results = re.sub(r'(<\?xml.+\?>)','',results,1)

            results = re.sub(r'xmlns=""','',results)

            #TODO: cache it!!
            if settings.cache:
                del xslt
            del dom
            del result_dom
        else:
            results = c


        if raw:
            results = c['response']

        time_total = time.time() - time_start

        if settings.debug and False:
            time_end = time.time()
            # END, at last that is the end

            summ = time_end - time_start
            print "\n\n"
            print "START MOMENT  - timestamp=%f; from_start=%fs (%d%%)"%(time_start, 0, 0)
            print "CALL MOMENT   - timestamp=%f; from_start=%fs (%d%%)"%(time_call, time_call-time_start, int((time_call-time_start)*100/summ))
            print "DUMP MOMENT   - timestamp=%f; from_start=%fs (%d%%)"%(time_dump, time_dump-time_start, int((time_dump-time_start)*100/summ))
            print "PROC MOMENT   - timestamp=%f; from_start=%fs (%d%%)"%(time_proc, time_proc-time_start, int((time_proc-time_start)*100/summ))
            print "FINISH MONENT - timestamp=%f; from_start=%fs (%d%%)"%(time_end, time_end-time_start, int((time_end-time_start)*100/summ))
            print "\n"
            print "PRE-CALL PROCESS  : time taken %fs (%d%% of total)"%(time_call-time_start, int((time_call-time_start)*100/summ))
            print "WAITING PROCESS   : time taken %fs (%d%% of total)"%(time_dump-time_call, int((time_dump-time_call)*100/summ))
            print "DUMPING PROCESS   : time taken %fs (%d%% of total)"%(time_proc-time_dump, int((time_proc-time_dump)*100/summ))
            print "PROCESSING PROCESS: time taken %fs (%d%% of total)"%(time_end-time_proc, int((time_end-time_proc)*100/summ))
            print "\nExpected productivity: %.1d pages/second"%(1/(time_end-time_start))
            print "\n\n"

        #if settings.debug:
        #     print results

        response = HttpResponse(results,[('Content-Type',content_type)])
        self.func_self.cookies.cookize(response)
        return response



class html_render(generic_decorator):
    def __call__(self,  template,
                        format=True,
                        debug=False,
                        root_tag="data"):

        path = settings.searchpath
        path = os.path.abspath(os.path.join(path, template))

        dumper = XML_Dumper(root_tag)

        time_call = time.time()
        self.func_self.cookies = Cookies()
        c = self.orig_func(**self.func_kwargs) or {}
        time_call_elapsed = time.time() - time_call

        time_dump = time.time()
        dom =  dumper.to_dom(**c)
        time_dump_elapsed = time.time() - time_dump

        if settings.debug:
            print dom.serialize(format=True, encoding=settings.charset)

        time_proc = time.time()

        xslt = Xslt(path)

        result_dom = xslt.apply_to_doc(dom)

        results = result_dom.serialize(format=format, encoding=settings.charset)
        time_proc_elapsed = time.time() - time_proc

        del dom
        del result_dom

        if settings.debug:
            print "Time profiling. xml dump: %f, xslt proc %f, call time %f, total %f"%(time_dump_elapsed,
                                                                                        time_proc_elapsed,
                                                                                        time_call_elapsed,
                                                                                        time_dump_elapsed+time_proc_elapsed+time_call_elapsed)
        return results

