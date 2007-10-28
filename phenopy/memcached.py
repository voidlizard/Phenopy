from decorators import generic_decorator
from misc import any_class
import memcache
import cPickle, sys, os

class settings(object):
    url = '127.0.0.1:11211'

#FIXME: remove hardcode
_cache = memcache.Client([settings.url], debug=0)

class memcached(generic_decorator):
    def __call__(self, cache_key, expire=0):
        res = _cache.get(cache_key)
        
        if not res:
            res = self.orig_func(**self.func_kwargs) or {}
            _cache.set(cache_key, res, expire)
        
        return res

