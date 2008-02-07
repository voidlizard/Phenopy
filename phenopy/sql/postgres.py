from contextlib import contextmanager
import psycopg2
from psycopg2.extras import DictCursor
import sys, os
from phenopy.sql.common import *

@contextmanager
def transaction(conn):
    try:
        yield None
    except:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        pass

# PostgreSQL-specific
def seq(table):
    return '%s_pk_seq'%table

def next_pk(table):
    return "nextval('%s')"%seq(table)

class Row(object):pass

class DAO(object):

    def __init__(self, conn, row_class=Row):
        self.conn = conn
        self.row_class = row_class
        self.pkset = pkset(self.metadata)

    def execute(self, query):
        curs = self.conn.cursor()
        curs.execute(query)

    def delete(self, criteria):
        curs = self.conn.cursor()
        dl = delete(self.metadata.__table__, criteria)
        curs.execute(str(dl), where_vals(criteria))


    def update(self, criteria, **values):
        curs = self.conn.cursor()
        upd = update(self.metadata.__table__, criteria, **values)
        vals = [v for k,v in upd.values.iteritems()]
        curs.execute(str(upd), vals + where_vals(criteria))

    def has_primary_key(self, kw):
        return False

    def auto_primary_key_enabled(self):
        return len(self.pkset) == 1

    def insert_vals_auto_primary_key(self):
        return next_pk(self.metadata.__table__)

    def insert_cols_primary_key(self):
        return list(self.pkset)[0]

    def create(self, fetch_id=True, **kw):
        curs = self.conn.cursor()
        cols = ins_cols(kw)
        vals = ins_vals(kw)
        v = []
        v += [x for x in repeat('%s', len(kw))]

        if not self.has_primary_key(kw) and self.auto_primary_key_enabled():
            cols.append( self.insert_cols_primary_key() )
            v.append( self.insert_vals_auto_primary_key() )

        ins = insert(self.metadata.__table__, cols, v)
        curs.execute(str(ins), vals)
        if fetch_id and self.auto_primary_key_enabled():
            s = seq(self.metadata.__table__)
            curs.execute('''select currval('%s')'''%s)
            return curs.fetchone()[0]
        return None        

    def iter_all(self, criteria=None, limit=None, offset=None):
        if limit or offset:
            return self.paged_iter(select(self.metadata.__table__, cols(self.metadata), criteria), limit, offset, *where_vals(criteria))
        return self.iter(select(self.metadata.__table__, cols(self.metadata), criteria), *where_vals(criteria))

    def iter(self, query, *bindparams):
        curs = self.conn.cursor(cursor_factory=DictCursor)
        curs.execute(str(query), bindparams)
        for p in curs.fetchall():
            proj = self.row_class()
            proj.__dict__.update(dict(p.items()))
            yield proj

    def paged_iter(self, query, limit, offset, *bindparams):
        assert((limit is not None and offset is not None) or (limit is None and offset is None))
        q = str(query) + " limit %s offset %s "
        curs = self.conn.cursor(cursor_factory=DictCursor)
        curs.execute(q, bindparams + tuple([limit, offset]))
        for p in curs.fetchall():
            proj = self.row_class()
            proj.__dict__.update(dict(p.items()))
            yield proj

    def get(self, criteria):
        curs = self.conn.cursor(cursor_factory=DictCursor)
        s = select(self.metadata.__table__, cols(self.metadata), criteria)
        curs.execute(str(s), where_vals(criteria))
        row = curs.fetchone()
        if not row:
            return None
        p = self.row_class()
        p.__dict__.update(row.items())
        return p

    def getby(self, query, *bind):
        curs = self.conn.cursor(cursor_factory=DictCursor)
        curs.execute(str(query), bind)
        row = curs.fetchone()
        if not row:
            return None
        p = self.row_class()
        p.__dict__.update(row.items())
        return p


    def count(self, query, *params):
        qq = '''
            select count(1) as count from (
                %s
            ) as sub1
        ''' % (query)
        res = self.getby(qq, *params)
        if res:
            return res.count
        return 0

