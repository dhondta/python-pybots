#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Simple utility objects related to API's.

"""
import types
from datetime import datetime, timedelta
from functools import wraps
from inspect import getargspec, getmembers
from six import with_metaclass
from time import sleep, time
from tinyscript.helpers.data.types import is_method

from ..protocols.http import JSONBot


__all__ = __features__ = ["apicall", "cache", "from_cache", "invalidate",
                          "private", "time_throttle", "API", "APIError",
                          "APIObject"]

TIME_THROTTLING    = {}

from_cache = lambda s, n: getattr(s, "_api_cache", {}).get(n)


def _id(something):
    try:
        return hash(something)
    except TypeError:
        return id(something)


def _result(f, self, *args, **kwargs):
    """
    Proxy function to return the result of a method and, if the result is None,
     in some different use cases, return something.
    """
    r = f(self, *args, **kwargs)
    if r is None and JSONBot in self.__class__.__bases__:
        r = self.json
    if isinstance(r, dict):
        err = r.get('error')
        if err is not None:
            raise APIError(err)
    return r


def apicall(f):
    """
    Dummy API method decorator for marking a method as an API call.
    """
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
        return _result(f, self, *args, **kwargs)
    g = f
    while hasattr(g, "__wrapped__"):
        g = g.__wrapped__
    g.__apicall__ = True
    return _wrapper


def cache(timeout=300):
    """
    API method decorator for caching or getting the cached result.
    """
    def _wrapper(f):
        spec = getargspec(f)
        multi = len(spec.args) == 1 and spec.varargs is not None
        @wraps(f)
        def _subwrapper(self, *args, **kwargs):
            self = getattr(self, "_parent", self)
            if not self._disable_cache:
                force = kwargs.pop('force', False)
                # handle varargs by searching for or writing each item in the
                #  cache, letting the request grouped with non-cached items
                if multi:
                    entries, tmp = {}, []
                    for item in args:
                        entry = self.from_cache(f, (item, ), kwargs)
                        if entry is None:
                            tmp.append(item)
                        else:
                            entries[item] = entry
                    args = tuple(tmp)
                    if len(args) > 0:
                        entries.update(_result(f, self, *args, **kwargs))
                        for i, e in self.json.items():
                            self.to_cache(f, (i, ), kwargs, timeout, entry=e)
                    return entries
                else:
                    entry = self.from_cache(f, args, kwargs)
                    return self.to_cache(f, args, kwargs, timeout) \
                           if entry is None or force else entry
            else:
                l = getattr(self, "logger", None)
                if l:
                    l.debug("Cache disabled")
                return _result(f, self, *args, **kwargs)
        return _subwrapper
    return _wrapper


def invalidate(*other_f):
    """
    API method decorator for invalidating the cached result of another API
     method.
    """
    def _wrapper(inner_f):
        @wraps(inner_f)
        def _subwrapper(self, *args, **kwargs):
            n = self.__class__.__name__
            s = getattr(self, "_{}__parent".format(n), self)
            cls = s.__class__
            #f = getattr(c, "_{}__api_registry".format(c.__name__))[other_f]
            try:
                return inner_f(self, *args, **kwargs)
            finally:
                c = self._api_cache
                for f in other_f:
                    fid = _id(cls.__api_registry[f])
                    if c.get(i) is not None:
                        c[i] = {}
                        l = getattr(self, "logger", None)
                        if l:
                            l.debug("Invalidated cache entry for '%s'" % f)
        return _subwrapper
    return _wrapper


def private(f):
    """
    API method decorator for checking if an API method is public based on a
     'public' attribute.
    """
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
        if not self.public:
            raise APIError("Only available in the private API")
        return f(self, *args, **kwargs)
    return _wrapper


def time_throttle(seconds, requests=1):
    """
    API method decorator for setting time throttling on a request method.
    
    :param seconds:  time frame in which the the maximum number of requests
                      can be achieved
    :param requests: maximum number of requests during the time frame
    """
    def _wrapper(f):
        @wraps(f)
        def _subwrapper(self, *args, **kwargs):
            if not getattr(self, "_disable_time_throttling", False):
                c = self.__class__
                TIME_THROTTLING.setdefault(c, [])
                t = TIME_THROTTLING[c]
                while len(t) > 0 and time() - t[0] >= seconds:
                    t.pop(0)
                while len(t) >= requests:
                    sleep(seconds - time() + t[0])
                    t.pop(0)
            r = f(self, *args, **kwargs)
            if not getattr(self, "_disable_time_throttling", False):
                TIME_THROTTLING[c].append(time())
            return r
        return _subwrapper
    return _wrapper


class MetaAPI(type):
    def __new__(meta, name, bases, clsdict, subcls=None):
        subcls = subcls or type.__new__(meta, name, bases, clsdict)
        if subcls.__name__ == "API":
            return subcls
        subcls.__api_registry = {}
        for k, f in getmembers(subcls):
            g = f
            while hasattr(g, "__wrapped__"):
                g = g.__wrapped__
            if not hasattr(g, "__apicall__"):
                continue
            n = f.__name__
            # keep function's reference associated to its original name
            subcls.__api_registry[n] = f
            # tokenize the name and create a tree of APIObjects with the tokens
            ftype, tokens = "get", n.split("_")
            if tokens[-1] == "DEL":
                tokens, ftype = tokens[:-1], "del"
            elif tokens[-1] == "SET":
                tokens, ftype = tokens[:-1], "set"
            o = subcls
            for i, token in enumerate(tokens):
                if i != len(tokens) - 1:
                    if not hasattr(o, token):
                        setattr(o, token, APIObject())
                    o = getattr(o, token)
                else:
                    delattr(subcls, k)
                    fc = getattr(o, token, None)
                    if fc is None:                        
                        fc = APIObject()
                        fc.__doc__ = f.__doc__
                        setattr(o, token, fc)
                    if ftype == "get":
                        fc._APIObject__get = types.MethodType(f, fc)
                    elif ftype == "set":
                        fc._APIObject__set = types.MethodType(f, fc)
                    elif ftype == "del":
                        fc._APIObject__del = types.MethodType(f, fc)
        subcls._disable_cache = False
        subcls._disable_time_throttling = False
        return subcls


class API(with_metaclass(MetaAPI, object)):
    """
    API class, for handling child attributes as instances of APIObject's.
    """
    _instances = {}
    _shared_attrs = ["_disable_cache", "_get", "from_cache", "to_cache"]
    
    def __init__(self, apikey, **kwargs):
        self._api_cache = {}
        self._api_key = apikey
        self._disable_cache = kwargs.pop('disable_cache', False)
        self._disable_time_throttling = kwargs.pop('disable_time_throttling',
                                                   False)
        for k, v in getmembers(self):
            if isinstance(v, APIObject):
                v._parent = self
    
    def from_cache(self, f, args=(), kwargs={}):
        if not self._disable_cache:
            id_f, id_a = API.ids(f, args, kwargs)
            c = self._api_cache
            c.setdefault(id_f, {})
            entry = c[id_f].get(id_a)
            if entry is not None and (entry[0] - datetime.now()).seconds >= 0:
                l, r = getattr(self, "logger", None), entry[1]
                if l:
                    l.debug("Got result of '%s' from cache" % f.__name__)
                if isinstance(r, dict):
                    err = r.get('error')
                    if err is not None:
                        raise APIError(err)
                return r
    
    def to_cache(self, f, args=(), kwargs={}, timeout=300, entry=None):
        if not self._disable_cache:
            id_f, id_a = API.ids(f, args, kwargs)
            c = self._api_cache
            c.setdefault(id_f, {})
            entry = entry or _result(f, self, *args, **kwargs)
            c[id_f][id_a] = (datetime.now() + timedelta(seconds=timeout), entry)
            l = getattr(self, "logger", None)
            if l:
                l.debug("Cached result of '%s'" % f.__name__)
            return entry
    
    def toggle_caching(self):
        self._disable_cache = not self._disable_cache
    
    def toggle_time_throttling(self):
        self._disable_time_throttling = not self._disable_time_throttling
    
    @staticmethod
    def ids(f, args, kwargs):
        id_f, id_a = _id(f), ()
        for a in args:
            id_a += (_id(a), )
        for k, w in kwargs.items():
            id_a += (_id("{}={}".format(k, _id(v))), )
        return id_f, id_a


class APIError(Exception):
    pass


class APIObject(object):
    """ Dummy API object class, for binding under the main API class. """
    def __init__(self):
        self.__parent = None
    
    def __call__(self, *args, **kwargs):
        if hasattr(self, "_APIObject__set") and \
            (len(args) == 0 or not hasattr(self, "_APIObject__get")):
            return self.__set(*args, **kwargs)
        elif hasattr(self, "_APIObject__get"):
            return self.__get(*args, **kwargs)
    
    def __del__(self):
        if hasattr(self, "_APIObject__del"):
            return self.__del()
    
    def __getattr__(self, name):
        a = self.__dict__.get(name)
        if a:
            return a
        p = self.__dict__.get('_APIObject__parent')
        a = getattr(p, name, None) if name in API._shared_attrs else None
        if a is None:
            raise AttributeError("'{}' object has no attribute '{}'"
                                 .format(p.__class__.__name__, name))
        return a
    
    @property
    def _parent(self):
        return self.__parent
    
    @_parent.setter
    def _parent(self, parent):
        self.__parent = parent
        for a in self.__dict__.values():
            if isinstance(a, APIObject):
                a._parent = parent
