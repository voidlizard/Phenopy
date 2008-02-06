from decorators import generic_decorator
from misc import any_class
import memcache
import cPickle, sys, os
import md5

class settings(object):
    url = '127.0.0.1:11211'
    enable_cache = True

#FIXME: remove hardcode
_cache = memcache.Client([settings.url], debug=0)

class memcached(generic_decorator):
    def __call__(self, cache_key, expire=0):
        res = _cache.get(cache_key)
        
        if not res:
            res = self.orig_func(**self.func_kwargs) or {}
            _cache.set(cache_key, res, expire)
        
        return res

class argcached(generic_decorator):
    def __call__(self, cache_keys=[], expire=0):

	if not settings.enable_cache:
	    return self.orig_func(**self.func_kwargs) or {}

	key = ""
	if len(cache_keys):
	    keynames = cache_keys
	else:
	    keynames = self.func_kwargs.keys()
	keynames.sort()
        for p in keynames:
		if (p in self.func_kwargs) and (p != 'self'):
    		    val = self.func_kwargs[p]
		    try:
    	    	        len(val)
	    		val.sort()
    		    except:
		        pass
		    key = key + str(val)

	key = self.orig_func.__name__ + "_" + md5.md5(key).hexdigest()
        res = _cache.get(key)


        if not res:
            res = self.orig_func(**self.func_kwargs) or {}
            _cache.set(key, res, expire)

        return res
