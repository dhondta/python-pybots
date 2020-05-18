# -*- coding: UTF-8 -*-
"""Client-side API dedicated to PwnedPasswords API.

"""
import hashlib
import random
from six import b

from ...core.utils.api import *


__all__ = ["PwnedPasswordsAPI"]


class PwnedPasswordsAPI(API):
    """
    HaveIBeenPwnedAPI class for communicating with the API of HaveIBeenPwned.
    
    Reference: https://haveibeenpwned.com/API/v3

    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://api.pwnedpasswords.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(PwnedPasswordsAPI, self).__init__(None, **kwargs)
    
    # Searching by range
    @time_throttle(1, 1000)
    @apicall
    @cache(3600)
    def count(self, password):
        """
        Search for a password according to a k-Anonymity model.
        
        :param password: password to be searched for
        """
        h = hashlib.sha1(b(password)).hexdigest().upper()
        self._request("/range/%s" % h[:5])
        hashes = self._response.text.split("\n")
        random.shuffle(hashes)
        for l in hashes:
            hash_suffix, count = l.split(":")
            if h[5:] == hash_suffix:
                return int(count)
        return 0
    
    def counts(self, *passwords):
        """
        Search for a password according to a k-Anonymity model.
        
        :param passwords: passwords to be searched for
        """
        r = {}
        for p in passwords:
            r[p] = self.count(p)
        return r
