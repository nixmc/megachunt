import logging

from functools import wraps
from flask import request
from werkzeug.contrib.cache import GAEMemcachedCache

cache = GAEMemcachedCache()

def cached(timeout=15 * 60, key='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            logging.info("Looking for %s in cache" % cache_key)
            rv = cache.get(cache_key)
            if rv is not None:
                logging.info("Found %s in cache" % cache_key)
                return rv
            rv = f(*args, **kwargs)
            logging.info("Putting %s in cache" % cache_key)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def noop(f):
    def wrapper(*args, **kwargs):
        logging.info("This begins decoration! " + request.path)
        return f(*args, **kwargs)
    return wraps(f)(wrapper)
