#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Simple utility objects related to API's.

"""
import random
import re
import types
from datetime import datetime, timedelta
from functools import wraps
from inspect import getmembers, unwrap
from six import with_metaclass
from time import sleep, time
try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec

from ..protocols.http import HTTPBot, JSONBot

SEARCH_BACKENDS = []
try:
    import jmespath
    SEARCH_BACKENDS.append("jmespath")
except ImportError:
    pass
try:
    import jsonpath
    SEARCH_BACKENDS.append("jsonpath")
except ImportError:
    pass
try:
    import yaql
    SEARCH_BACKENDS.append("yaql")
except ImportError:
    pass


__all__ = __features__ = ["apicall", "cache", "invalidate", "private", "time_throttle", "API", "APIError", "APIObject",
                          "SearchAPI"]

TIME_THROTTLING = {}


def _id(something):
    """
    Small utility function to compute the ID of anything.
    
    :param something: any object
    """
    try:
        return hash(something)
    except TypeError:
        return id(something)


def _result(f, self, *args, **kwargs):
    """
    Proxy function to return the result of a method and, if the result is None, in some different use cases, return
     something.
    """
    s = getattr(self, "_parent", self)
    r = f(s, *args, **kwargs)
    if r is None:
        r = s._json
    if isinstance(r, dict):
        err = r.get('error')
        if err is not None and all(m not in err for m in getattr(s, "no_error", [])):
            code = r.get('status') or r.get('code') or r.get('statusCode') or r.get('status_code')
            raise APIError(err, code)
    return r


def apicall(f):
    """
    Dummy API method decorator for flagging a method as an API call.
    """
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
        return f(getattr(self, "_parent", self), *args, **kwargs)
    unwrap(f).__apicall__ = True
    return _wrapper


def cache(timeout=300, retries=1):
    """
    API method decorator for caching or getting the cached result.
    """
    def _wrapper(f):
        spec = getargspec(f)
        multi = len(spec.args) == 1 and spec.varargs is not None
        @wraps(f)
        def _subwrapper(self, *args, **kwargs):
            if multi and len(args) == 0:
                return
            s = getattr(self, "_parent", self)
            if not s._disable_cache:
                force = kwargs.pop('force', False)
                # handle varargs by searching for or writing each item in the cache, letting the request grouped with
                #  non-cached items
                if multi:
                    entries, tmp = {} if s._kind == "json" else [], []
                    for item in args:
                        entry = s._from_cache(f, (item, ), kwargs)
                        if entry is None or \
                           isinstance(entry, dict) and len(entry) == 1 and list(entry.values())[0] is None:
                            tmp.append(item)
                        elif isinstance(entry, dict):
                            entries.update(entry)
                        elif isinstance(entries, dict):
                            entries[item] = entry
                        elif isinstance(entries, list):
                            entries.append(entry)
                    n = retries
                    while len(tmp) > 0 and n > 0:
                        r = _result(f, s, *tmp, **kwargs)
                        for i, e in (r.items() if isinstance(r, dict) else zip(tmp, r if s._kind == "json" else [r]
                                     if len(tmp) == 1 else r.strip("\n"))):
                            if e is None:
                                continue
                            s._to_cache(f, (i, ), kwargs, timeout, entry=e)
                            tmp.remove(i)
                            if s._kind == "json":
                                entries[i] = e
                            else:
                                entries.append(e)
                        n -= 1
                    return entries
                else:
                    entry = s._from_cache(f, args, kwargs)
                    if entry is None or force:
                        entry = s._to_cache(f, args, kwargs, timeout)
                    return entry
            else:
                s._logger.debug("Cache disabled")
                return _result(f, s, *args, **kwargs)
        return _subwrapper
    return _wrapper


def invalidate(*other_f):
    """
    API method decorator for invalidating the cached result of another API method.
    """
    def _wrapper(inner_f):
        @wraps(inner_f)
        def _subwrapper(self, *args, **kwargs):
            s = getattr(self, "_parent", self)
            try:
                return inner_f(s, *args, **kwargs)
            finally:
                f = unwrap(inner_f)
                if getattr(f, "_api_cache_hit", False):
                    delattr(f, "_api_cache_hit")
                else:
                    c = s._api_cache
                    for f in other_f:
                        # the current class may be inherited from an API class, which can be itself inherited ; so,
                        #  recurse on class' base to find the API registry where f's reference is located
                        fid, cls = None, s.__class__
                        while hasattr(cls, "_MetaAPI__api_registry"):
                            try:
                                fid = _id(s.__class__._MetaAPI__api_registry[f])
                                break
                            except KeyError:
                                cls = cls.__bases__[0]
                        if c.get(fid) is not None:
                            c[fid] = {}
                            s._logger.debug("Invalidated cache entry for '%s'" % f)
        return _subwrapper
    return _wrapper


def private(f):
    """
    API method decorator for checking if an API method is public based on a 'public' attribute.
    """
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
        if self.public:
            raise APIError("Only available in the private API")
        return f(self, *args, **kwargs)
    return _wrapper


def time_throttle(seconds_low, seconds_high=None, requests=1):
    """
    API method decorator for setting time throttling on a request method.
    
    NB: this should be put before '@apicall' and '@cache'.
    
    :param seconds_low:  low limit for the time frame in which the maximum number of requests can be achieved
    :param seconds_high: high limit for the time frame
    :param requests:     maximum number of requests during the time frame
    """
    def _wrapper(f):
        @wraps(f)
        def _subwrapper(self, *args, **kwargs):
            if not getattr(self, "_disable_time_throttling", False):
                seconds = seconds_low if seconds_high is None or seconds_low <= seconds_high else \
                          random.uniform(seconds_low, seconds_high)
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
    """
    API metaclass, for handling child attributes as instances of APIObject's.
    """
    def __new__(meta, name, bases, clsdict, subcls=None):
        subcls = subcls or type.__new__(meta, name, bases, clsdict)
        if subcls.__name__ == "API":
            return subcls
        subcls.__api_registry = {}
        for k, f in getmembers(subcls):
            g = unwrap(f)
            if not hasattr(g, "__apicall__"):
                continue
            n = f.__name__
            # keep function's reference associated to its original name
            subcls.__api_registry[n] = g
            # tokenize the name and create a tree of APIObjects with the tokens
            o, tokens = subcls, n.split("_")
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
                    fc._APIObject__get = f # types.MethodType(f, fc)
        subcls._disable_cache = False
        subcls._disable_time_throttling = False
        return subcls


class API(with_metaclass(MetaAPI, object)):
    """
    API class, for managing cache.
    
    :param key:                     API key
    :param url:                     API URL
    :param kind:                    http|json
    :param disable_cache:           whether it should be initialized without caching
    :param disable_time_throttling: whether it should be initialized without time throttling
    """
    def __init__(self, key, url=None, kind="json", disable_cache=False, disable_time_throttling=False, **kwargs):
        self._api_cache = {}
        self._api_key = key
        self._disable_cache = disable_cache
        self._disable_time_throttling = disable_time_throttling
        self._kind = kind
        # transform every apicall-decorated method to API objects ; this allows to decompose methods into a hierarchy of
        #  bound objects, e.g. bot.search_host_info => bot.search.host.info
        for k, v in getmembers(self):
            if isinstance(v, APIObject):
                v._parent = self
        # then select and initialize the underlying bot
        if kind not in ["http", "json"]:
            raise ValueError("bad API type")
        botcls = [HTTPBot, JSONBot][kind == "json"]
        self.__bot = botcls(url or self.url, **kwargs)
    
    def __enter__(self):
        """ Context manager enter method, executing after __init__. """
        self.__bot.__enter__()
        return self
    
    def __exit__(self, *args, **kwargs):
        """ Context manager exit method, for gracefully closing the bot. """
        self.__bot.__exit__(*args, **kwargs)
    
    def _check_apikey(self, msg="missing API key", code=401):
        """ API key check function. """
        if not self._api_key:
            raise APIError(msg, code)
    
    def _from_cache(self, f, args=(), kwargs={}):
        """ Cache request method. """
        if not self._disable_cache:
            id_f, id_a = API._ids(f, args, kwargs)
            c = self._api_cache
            c.setdefault(id_f, {})
            entry = c[id_f].get(id_a)
            if entry is not None and (entry[0] - datetime.now()).seconds >= 0:
                r = entry[1]
                self._logger.debug("Got result of '%s' from cache" % f.__name__)
                if isinstance(r, dict):
                    err = r.get('error')
                    if err is not None:
                        raise APIError(err)
                unwrap(f)._api_cache_hit = True
                return r
    
    def _request(self, *args, **kwargs):
        """ Binding to bot's request method. """
        return self.__bot.request(*args, **kwargs)
    
    def _to_cache(self, f, args=(), kwargs={}, timeout=300, entry=None):
        """ Cache record method. """
        if not self._disable_cache:
            id_f, id_a = API._ids(f, args, kwargs)
            c = self._api_cache
            c.setdefault(id_f, {})
            entry = entry or _result(f, self, *args, **kwargs)
            c[id_f][id_a] = (datetime.now() + timedelta(seconds=timeout), entry)
            self._logger.debug("Cached result of '%s'" % f.__name__)
            return entry
    
    def _toggle_caching(self):
        self._disable_cache = not self._disable_cache
    
    def _toggle_time_throttling(self):
        self._disable_time_throttling = not self._disable_time_throttling
    
    @property
    def _config(self):
        return self.__bot.config
    
    @property
    def _json(self):
        r = getattr(self.__bot, "json", None)
        if r is None:
            raise APIError("No response from {} ; check that the server still responds".format(self.__bot.url))
        return r
    
    @property
    def _logger(self):
        return self.__bot.logger
    
    @property
    def _response(self):
        return getattr(self.__bot, "response", None)
    
    @property
    def _session(self):
        return self.__bot.session
    
    @property
    def _soup(self):
        return getattr(self.__bot, "soup", None)
    
    @staticmethod
    def _ids(f, args, kwargs):
        id_f, id_a = _id(f), ()
        for a in args:
            id_a += (_id(a), )
        for k, v in kwargs.items():
            id_a += (_id("{}={}".format(k, _id(v))), )
        return id_f, _id(id_a)


class APIError(Exception):
    def __init__(self, message, code=None):
        if code:
            message = "{} ({})".format(message, code)
        super(APIError, self).__init__(message)


class APIObject(object):
    """ Dummy API object class, for binding under the main API class. """
    def __init__(self):
        self.__parent = None
    
    def __call__(self, *args, **kwargs):
        if hasattr(self, "_APIObject__get"):
            return self.__get(self.__parent, *args, **kwargs)
    
    def __getattr__(self, name):
        a = self.__dict__.get(name)
        if a:
            return a
        p = self.__dict__.get('_APIObject__parent')
        a = getattr(p, name, None)
        if a is None:
            raise AttributeError("'{}' object has no attribute '{}'".format(p.__class__.__name__, name))
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


class SearchAPI(API):
    """
    SearchAPI class, for managing cache and a search feature relying on multiple backends.

    :param key:                     API key
    :param url:                     API URL
    :param kind:                    http|json
    :param disable_cache:           whether it should be initialized without caching
    :param disable_time_throttling: whether it should be initialized without time throttling
    :param search_backend:          search backend to be used
    """
    def __init__(self, key, url=None, kind="json", disable_cache=False, disable_time_throttling=False,
                 search_backend=None, **kwargs):
        self.__backend = search_backend
        super(SearchAPI, self).__init__(key, url, kind, disable_cache, disable_time_throttling, **kwargs)
    
    def _search(self, query):
        query = str(query)
        if self.__backend == "jmespath":
            return jmespath.search(query, self._json)
        elif self.__backend == "yaql":
             return self.__engine(query).evaluate(data=self._json)
        elif self.__backend == "jsonpath":
            return jsonpath.jsonpath(self._json, query) or []
        else:
            if "(?i)" not in query:
                query = "(?i)" + query
            r = []
            for record in self._json['data']:
                for _, v in record.items():
                    if re.search(query, str(v)):
                        r.append(record)
            return r
    
    @property
    def backend(self):
        return self.__backend
    
    @backend.setter
    def backend(self, value):
        if value and value not in SEARCH_BACKENDS:
            raise ValueError("Bad search backend")
        if value == "yaql":
            self.__engine = yaql.factory.YaqlFactory().create()
        self.__backend = value

