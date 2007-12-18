
class configuration_error(Exception):
    pass

class configuration(object):
    def __init__(self, name):
        mod = __import__("config.%s"%name, fromlist=['config'])
        self.proxied = getattr(mod, 'config')

    def __getattr__(self, name):
        return getattr(self.proxied, name)

