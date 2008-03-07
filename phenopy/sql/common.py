from itertools import *

class insert(object):
    def __init__(self, table, columns, values):
        self.table = table
        self.columns = columns
        self.values = values

    def __str__(self):
        return '''insert into %s (%s) values (%s)'''%( self.table,
                                                       ", ".join(self.columns),
                                                       ", ".join(self.values))
class select(object):
    def __init__(self, table, columns, where=None, orderby=[]):
        self.table = table
        self.columns = columns
        self.where = where
        self.orderby = orderby

    def __str__(self):
        s =  '''select %s from %s'''%(",".join(self.columns), self.table)
        if self.where:
            s += ' where %s'%where(self.where)
        if len(self.orderby):
            s += ' ' + ' '.join(['order by %s %s'%(a,b) for (a,b) in self.orderby])
        return s

class delete(object):
    def __init__(self, table, where=None):
        self.table = table
        self.where = where

    def __str__(self):
        s =  '''delete from %s'''%(self.table)
        if self.where:
            s += ' where %s'%where(self.where)
        return s        

class update(object):
    def __init__(self, table, where=None, **kw):
        self.table = table
        self.where = where
        self.values = kw

    def __str__(self):
        s =  '''update %s'''%(self.table)
        cols = ', '.join([('%s = %%s'%(k)) for k,v in self.values.iteritems()])
        s += ' set ' + cols
        if self.where:
            s += ' where %s'%where(self.where)
        return s 


class column(object):
    def __init__(self, primary_key=False):
        self.primary_key = primary_key

def cols(klass):
    return [c for c,t in klass.__dict__.iteritems() if t.__class__ == column]

def ins_cols(arr):
    return [ k for k,v in arr.iteritems() ]

def ins_vals(arr):
    return [ v for k,v in arr.iteritems() ]

def cols_l(klass):
    return ", ".join(cols(klass))

def pkset(md):
    return set([k for k,v in md.__dict__.iteritems() if v.__class__ == column and v.primary_key])


def where(criteria):
    return criteria.part

def where_vals(criteria):
    if not criteria:
        return []
    return []+criteria.value


class binary_(object):
    def __init__(self, left, right):
        self.left = left 
        self.right = right

    @property
    def part(self):
        return (' %s '%(self.op)).join([self.left.part, self.right.part])

    @property
    def value(self):
        return [] + self.left.value + self.right.value

class and_(binary_):
    op = 'and'

class or_(binary_):
    op = 'or'

class in_(object):

    def __init__(self, col, *vals):
        self.col = col 
        self.value = [] + list(vals)
    
    @property
    def part(self):
        return '%s in(%s)'%(self.col, ', '.join('%s' for x in self.value))


class isnull(object):

    def __init__(self, col):
        self.col = col 
    
    @property
    def part(self):
        return '%s is NULL'%self.col

    @property
    def value(self):
        return []

class eq(object):

    def __init__(self, col, val):
        self.col = col
        self.value = [val]
    
    @property
    def part(self):
        return '%s = %%s'%self.col
