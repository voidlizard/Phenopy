# -*- coding: utf-8 -*-
import re, libxml2
import string, operator, array
import inspect

_names = {}

class XML_Dumper(object):
 
    def _dump_something(self, name = None, object = None, attribs={},parent_node = None):
        
        if object is None:
            return

        try:
            obj = object
            func = self._dump_item
            object_name = ''

            try:
                object_name = _names[name]
            except KeyError:
                object_name = self.re_repl_camel2.sub(lambda x:self.replace_tbl[x.group(1)], name)
                object_name = object_name.replace('_','-').lower()
                _names[name] = object_name 

            tp = type(object)
            nm = tp.__name__

            if obj.__class__.__base__ == list:
                func = self._dump_sequence
            elif tp == dict:
                func = self._dump_dict
            elif tp == tuple or tp == list or tp == tuple:
                func = self._dump_sequence

            if self.type_transforms.has_key(nm):
                obj = self.type_transforms[nm](object)
                tp = type(obj)
                nm = tp.__name__

            node  = parent_node.newChild(None, object_name, None)
            np = node.newProp
            for n,v in attribs.iteritems():
                np(n, str(v))

            if self.type_hooks.has_key(nm):
                self.type_hooks[nm](object, node)

            func(obj, node)

        except AttributeError:
            pass

    def _dump_sequence(self, object = None, parent_node = None):
        m1 = self._dump_something
        m2 = self._dump_object
        for x in object:
            m1("item", x, {}, parent_node)
        if hasattr(object, '__dict__'):
            m2(object, parent_node)

    def _dump_dict(self, object = None, parent_node = None):
        m = self._dump_something
        for nm,val in object.iteritems():
            m("item", val, {'key':nm}, parent_node)

    def _dump_item(self, object = None, parent_node = None):

        if hasattr(object, "__dict__"):
            if object.__class__.__name__ == 'CDATA':
                self._dump_CDATA_item(object, parent_node)
            else:
                self._dump_object(object, parent_node)
        else:
            parent_node.addContent(str(object))


    def _dump_CDATA_item(self, object, parent_node):
        cdata = self._xml_doc.newCDataBlock(object.content, len(object.content))
        parent_node.addChild(cdata)

    def _dump_object(self, obj = None, parent_node = None):
        parent_node.newProp('class', obj.__class__.__name__)
        ds = self._dump_something
        attr = obj.__dict__.keys() + [ x[0] for x in inspect.getmembers(obj.__class__) if type(x[1]) == property]
        for k in attr:
            ds(k, getattr(obj,k), {}, parent_node)

    def _dump_objects(self, parent_node = None, **kw):
        ds = self._dump_something
        for name, value in kw.iteritems():
            ds(name, value, {}, self._root_node)

    def _free_xml_doc(self):
        if self._xml_doc:
            self._xml_doc.freeDoc()
            self._xml_doc = None

    def _create_xml_doc(self):
        self._free_xml_doc()
        self._xml_doc = libxml2.newDoc('1.0')
        self._root_node = libxml2.newNode(self.root_tag_name)
        self._xml_doc.setRootElement(self._root_node)

    def __del__(self):
        self._free_xml_doc()

    def _make_tag_name(self, name):
        name = self.re_repl_camel2.sub(lambda x:self.replace_tbl[x.group(1)], name)
        name = name.replace('_','-')
        return name.lower()

    def to_dom(self, **kw):
        self._create_xml_doc()
        self._dump_objects(self._root_node, **kw)
        return self._xml_doc

    def to_string(self, encoding='utf-8', format=True, **kw):
        doc = self.to_dom(**kw)
        return doc.serialize(encoding=encoding, format=format)

    def __init__(self, root_tag="data", type_transforms=dict(), type_hooks=dict()):
        self.root_tag_name = root_tag
        self._xml_doc = None
#        self.re_repl_camel = re.compile(r'([a-z])([A-Z])')
        self.re_repl_camel2 = re.compile(r'([a-z][A-Z])')
        self.in_process = set()
        self.type_transforms = type_transforms
        self.type_hooks = type_hooks
        self.replace_tbl = dict(
                      ('%s%s' % (chr(a), chr(b)), '%s-%s' % (chr(a), chr(b))) 
                      for a in xrange(ord('a'), ord('z') + 1)
                      for b in xrange(ord('A'), ord('Z') + 1))


class SomeTestClass(object):
    pass

    def some_method(self):
        return True

    @property
    def get_some_property(self):
        return self.some_property

    def __init__(self):
        self.some_property = "some_value"
        self.another = None
        self.alsoOne = '222'

class Date_Time(object):
    pass

def date_time_wrapper(dt):
    fields = ('year', 'month', 'day', 'hour', 'minute', 'second')
    class date_time(object):
        def __init__(self, o):
            for x in fields:
                if hasattr(o, x):
                    setattr(self, x, getattr(o, x))
    return date_time(dt)

if __name__ == "__main__":
    import datetime

    x = XML_Dumper(type_transforms={datetime.datetime.__name__:lambda t: date_time_wrapper(t) },
                   type_hooks={datetime.datetime.__name__ :  lambda a,b: b.newProp('year', str(a.year))  })

    for i in xrange(0, 100):
        x.to_dom( sequence=[SomeTestClass() for i in xrange(0,100)] )
#        print x.to_string( sequence=[SomeTestClass() for i in xrange(0,100)] )
