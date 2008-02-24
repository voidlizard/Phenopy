# -*- coding: utf-8 -*-

def dump_atom( a ):
    if type(a) == int or type(a) == long:
        return str(a)
    elif type(a) == bool:
        return str(a).lower()
    elif a is None:
        return 'null'
    else: # type(a) == str or type(a) == unicode:
        return "'" + str(a).replace("\\","\\\\").replace("'","\\'") + "'"

def dump_element( el ):
    if hasattr(el, "__dict__"):
        return dump_object(el)
    elif type(el) == dict:
        return dump_dict(el)
    elif hasattr(el, "__iter__"):
        return dump_sequence(el)
    return dump_atom(el)

def dump_object( obj ):
    return dump_dict(obj.__dict__)

def dump_sequence( seq ):
    return '[' + ', '.join( dump_element(x) for x in seq ) + ']'

def dump_dict( d ):
    return '{' + ', '.join( ("'%s' : %s"%(k, dump_element(v)) for k,v in d.iteritems()) ) + '}'

def dump_assignment( left, right ):
    if left is not None:
        return left + ' = ' + dump_element( right )
    return dump_element( right )

class JSON_Dumper(object):
    def __init__(self, root=None):
        self.root = root

    def dump_dict(self, **objects):
        return dump_assignment( self.root, objects )

    def dump_object(self, x):
        return dump_assignment( self.root, x)

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

    class Obj(object):
        def __init__(self):
            self.sort = "id"
            self.totalRecords = 2
            self.recordsReturned = 2
            self.startIndex = 0
            self.dir = "asc"
            self.records = [
                { 
                "firstname":"ssss", 
                "created":"2007-12-26 16:45:56.806585", 
                "id":"1", 
                "secondname":"kkkk", 
                "active":"True", 
                "email":"kkk@kkk" 
                } 
            ]
   
    print
    print
    print x1.dump_object(Obj()) 
