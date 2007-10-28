# -*- coding: utf-8 -*-
import re, libxml2

class XML_Dumper(object):
   
    def _type(self, o):
        if hasattr(o.__class__,'__base__') and o.__class__.__base__ == list:
            return list
        return type(o)
 
    def _dump_something(self, name = None, object = None, attribs={},parent_node = None):
        
        if object is None:
            return

        obj = object
        try:
            obj = self.type_transforms[type(object).__name__](object)
        except KeyError:
            pass

        func = XML_Dumper._dump_item
        try:
            func = XML_Dumper.types[self._type(obj)]
        except KeyError:
            pass
        
        object_name = self._make_tag_name(name)

        if object_name is None:
            object_name = self._make_tag_name(obj.__class__.__name__)

        node  = parent_node.newChild(None, object_name, None)
        for n,v in attribs.items():
            node.newProp(n, str(v))
        
        try:
            self.type_hooks[type(object).__name__](object, node)
        except KeyError:
            pass


        func(self, obj, node)

    def _dump_sequence(self, object = None, parent_node = None):
        for x in object:
            self._dump_something(object=x, name="item", parent_node=parent_node)
        if hasattr(object, '__dict__'):
            self._dump_object(object = object, parent_node = parent_node)

    def _dump_dict(self, object = None, parent_node = None):
        for nm,val in object.items():
            self._dump_something(object=val, name="item", attribs={'key':nm}, parent_node=parent_node)

    def _dump_item(self, object = None, parent_node = None):

        if object is None:
            return

        if not self._is_available(object):
            return

        self._seize(object)

        if hasattr(object, "__dict__"):
            if object.__class__.__name__ == 'CDATA':
                self._dump_CDATA_item(object, parent_node)
            else:
                self._dump_object(object, parent_node)
        else:
            parent_node.addContent(str(object))

        self._release(object)

    def _dump_CDATA_item(self, object, parent_node):
        cdata = self._xml_doc.newCDataBlock(object.content, len(object.content))
        parent_node.addChild(cdata)

    def _dump_object(self, object = None, parent_node = None):

        parent_node.newProp('class', object.__class__.__name__)
        for name, value in object.__dict__.iteritems():
            self._dump_something(name=name,
                                 object=value,
                                 parent_node=parent_node)

    def _dump_objects(self, parent_node = None, **kw):
        for name, value in kw.iteritems():
            self._dump_something(name=name, object=value, parent_node = self._root_node)

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
        if name is None:
            return None
        
        nm = self.re_repl_camel.sub(lambda x:"%s-%s"%(x.group(1),x.group(2).lower()), name)
        nm = self.re_repl_underline.sub("-", nm)

        return str(nm).lower()

    def _seize(self, obj):
        self.in_process.add(id(obj))

    def _is_available(self, obj):
        return not (id(obj) in self.in_process)

    def _release(self, obj):
        self.in_process.remove(id(obj))

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
        self.re_repl_underline = re.compile(r'_')
        self.re_repl_camel = re.compile(r'([a-z])([A-Z])')
        self.in_process = set()
        self.type_transforms = type_transforms
        self.type_hooks = type_hooks

    types = {
            list  : _dump_sequence,
            tuple : _dump_sequence,
            set   : _dump_sequence,
            dict  : _dump_dict,
        }

class SomeTestClass(object):
    pass

    def some_method(self):
        return True

    @property
    def get_some_property(self):
        return self.some_property

    def __init__(self):
        self.some_property = "some_value"

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
    print x.to_string(  one=1,
                        two=2,
                        a_tuple=(1,2,3),
                        now = datetime.datetime.now(),
                        some_object=SomeTestClass(),
                        list_1_5=[1,2,3,4,5,(1,2)],
                        some_set=set([1,2,3,4,5,6,7,7,7,7]),
                        some_dict={1:3, "a":"b", 'lala':SomeTestClass(), 'list':[1,2,3,4],'tuple':(1,2,3)})

