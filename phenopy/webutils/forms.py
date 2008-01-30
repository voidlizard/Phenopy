import re

#TODO: to utilities
class Form_Data(object):

    def __init__(self, dict={}, transforms={}, **kw):
        checkboxes = {}
        chb = re.compile(r'(\w+):(\w+)')

        for k,v in kw.items():
            setattr(self, k, v)

        def tr(name, val):
            try:
                t = transforms[name]
            except KeyError:
                t = lambda x:x
            return t(val)

        for k,v in dict.items():
            m = chb.match(k)
            if m:
                name = m.group(1)
                val = m.group(2)
                if not checkboxes.has_key(name):
                    checkboxes[name] = set()
                checkboxes[name].add(val)
            else:
                setattr(self, k, tr(k,v))
        for k,v in checkboxes.items():
            setattr(self, k, tr(k,v))

class Form_Errors(object):
    def __init__(self, dict):
        for k,v in dict.items():
            setattr(self, k, v)
