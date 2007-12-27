# -*- coding: utf-8 -*-
import re, StringIO

class JSON_Dumper(object):
    def __init__(self, root=None):
        self.root = root
        self.io = StringIO.StringIO()

    def _acc(self, chunk):
        self.io.write(chunk)

    def dump_dict(self, **objects):
        if self.root:
            self._acc(self.root + " = {\n")

        for k,v in objects.iteritems():
            self._dump_something(k, v)

        if self.root:
            self._acc("\n}")
        
        self.io.flush()
        return self.io.getvalue()

    def dump_object(self, x):
        if self.root:
            self._acc(self.root + " = {\n")

        self._dump_something(None, x, 1)

        if self.root:
            self._acc("\n}")
        
        self.io.flush()
        return self.io.getvalue()


    def _dump_sequence(self, val, level=0):
        self._acc(" [\n")
        for x in val:
            self._dump_something(None, x, level+1)
        self._acc("  "*level+"],\n")

    def _dump_object(self, val, level):
        for k, v in val.__dict__.iteritems():
            self._dump_something(k, v, level+1)

    def _dump_dict(self, val, level=0):
        m = self._dump_something
        self._acc("  "*level+"{\n")
        for nm,o in val.iteritems():
            m('"'+nm+'"', o,  level+1)
        self._acc("  "*level+"},\n")

    def _dump_item(self, val, level=0):
        if not hasattr(val,"__dict__"):
            if val is None:
                self._acc('null,\n')
            else:
                self._acc('"%s",\n'%str(val))
        else:
            self._acc("{\n")
            self._dump_object(val, level+1)
            self._acc("  "*(level-1)+"},\n")

    def _dump_something(self, name, val, level=0):

        tp = type(val)
        func = self._dump_item
 
#        print name, val

        if name is not None:
            self._acc("  "*level + name + ":")
        else:
            self._acc("  "*level)

        if val.__class__.__base__ == list:
            func = self._dump_sequence
        elif tp == dict:
            func = self._dump_dict
        elif tp == tuple or tp == list or tp == tuple:
            func = self._dump_sequence

        #self._acc(name)
        func(val, level=level+1)

if __name__ == "__main__":
    import datetime

    class TestClass(object):
        pass

    class TestClass2(object):
        pass

    class TestClass3(object):
        pass

    tc = TestClass()
    tc2 = TestClass2()

    tc.one = TestClass2()
    tc.two = TestClass3()
    tc.two.three = "QQQ"
    tc.two.four = 4
    tc.two.five = [1,2,3,4,45,5,6, TestClass()]

    x = JSON_Dumper('data')
    # dump atoms
    print x.dump_dict(str="LALA", str2="BEBE", val1=22, val2=None, val4=-222.44)

    # dump lists 
    print x.dump_dict(val1=["LALA",2,3,4,"BEBE",["QQ", "ZZ"]])

    # dump dicts 
    print x.dump_dict(val1={"LALA":"QQ","TWO":"2"})

    # dump objects 
    print x.dump_dict(val1=tc, val2=tc2)

    x1 = JSON_Dumper()
    # dump dicts 
    print x1.dump_dict(val1={"LALA":"QQ","TWO":"2"})
    
    class Obj(object):
        def __init__(self):
            self.rows = [1,2,3,4,5,6]

    print x1.dump_object(Obj())

