
class Cookies(object):
   
    def __init__(self):
        self.cookies_ = []

    def add(self, name, value, domain=None, max_age=None, expires=None):
        self.cookies_.append( lambda s: s.set_cookie(name, value, domain=domain, max_age=max_age, expires=expires))

    #FIXME: BWA-HA-HA!
    def cookize(self, request):
        for c in self.cookies_:
            c(request)

