# -*- coding: UTF-8 -*-
"""Utility functions for other modules of this subpackage.

"""
import base64
import os
import re
import string
import urllib
from itertools import chain, product
from six import string_types
from subprocess import Popen, PIPE
from time import sleep, time


__all__ = ["base64", "bruteforce", "execute", "filter_sources", "os", "re",
           "string_types", "time_throttle", "urllib", "APIError"]

ALL_CHARS = list(map(chr, range(256)))
TIME_THROTTLING = {}


def bruteforce(max_len, alphabet=ALL_CHARS, from_zero=True):
    """
    Generator for bruteforcing according to a maximum length and an alphabet.
     2 behaviors are possible:
     - from_zero=True:  this will generate entries from length=1 to max_len
     - from_zero=False: this will generate entries of length=max_len only
    
    :yield: bruteforce entry
    """
    for i in range(*[1 if from_zero else max_len, max_len + 1]):
        for c in product(alphabet, repeat=i):
            yield c if isinstance(c[0], int) else ''.join(c)


def execute(cmd):
    """
    Simple wrapper for subprocess.Popen.
    
    :param cmd: command string
    """
    return Popen(cmd.split(), stdout=PIPE, stderr=PIPE).communicate()


def filter_sources(sources_list, netloc=None):
    """
    Selection function either for getting a shuffled list of selected sources or
     a single source filtered by its network location.

    :param sources: reference list of sources
    :param netloc:  network location of the source
    :return:        list of selected sources
    """
    if netloc is not None:
        sources = []
        for s in sources_list:
            if netloc == urlparse(s[1]).netloc:
                sources.append(s)
                break
    else:
        sources = [s for s in sources_list]
        random.shuffle(sources)
    return sources


def time_throttle(seconds, requests=1):
    """
    Decorator for setting time throttling on a request method.
    
    :param seconds:  time frame in which the the maximum number of requests can
                      be achieved
    :param requests: maximum number of requests during the time frame
    """
    def _wrapper(f):
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


class APIError(Exception):
    pass
