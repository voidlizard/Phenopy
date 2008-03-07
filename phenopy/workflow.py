from kjbuckets import kjGraph
from itertools import groupby
from operator import attrgetter

class transition(object):
    def __init__(self, a, b, name=None, role=None, priority=1):
        self.a = a
        self.b = b
        self.name = name
        self.role = role
        self.priority = priority


class Workflow(object):

    def __init__(self):
        self.trans   = {}
        self.acts = {}
        for key, transitions in groupby(self.workflow, attrgetter('role')):
            if not self.trans.has_key(key):
                self.trans[key] = kjGraph()
            for t in transitions:
                arch = (t.a, t.b)
                self.trans[key].add(arch)
                try:
                    self.acts[arch+(t.role,)] += t
                except KeyError:
                    self.acts[arch+(t.role,)] = t

    def available(self, a, b, role):
        return b in self.trans[role].neighbors(a)


    def action(self, a, b, role):
        return self.acts[(a,b,role)].name

    def actions(self, status, role):
        a = []
        for x in self.trans[role].neighbors(status):
            try:
                a.append( self.acts[(status, x, role)] )
            except KeyError:
                pass
        return a

