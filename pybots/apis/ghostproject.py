# -*- coding: UTF-8 -*-
"""Bot client dedicated to Nuclear Leaks.

"""
import cfscrape
import re
from tinyscript.helpers.data.types import *

from ..core.utils.api import *


__all__ = ["GhostProjectAPI"]


class GhostProjectAPI(API):
    """
    GhostProjectAPI class for communicating with the API of GhostProject.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    url = "https://ghostproject.fr"
    
    def __init__(self, **kwargs):
        super(GhostProjectAPI, self).__init__(None, **kwargs)
        s = self._session.headers
        #FIXME: get Cloudflare clearance cookie by following the protocol for
        #        DDoS protection
        s['Origin'] = self.url
        s['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        s['X-Requested-With'] = "XMLHttpRequest"
     
    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "email":
                email_address(v)
    
    def _request(self, query):
        """
        Generic post method.
        
        :param query: query string (email or domain with wildcard)
        """
        super(GhostProjectAPI, self)._request("/x000x1337.php", "post",
                                              data={'param': query})
        if self._response.status_code != 200:
            raise APIError(self._response.reason)
        lines = self._response.text.splitlines()
        t, d = lines[0], filter(lambda x: x != "", lines[1:])
        return {'time': t, 'data': {k.strip(): v.strip() for l in d \
                                               for k, v in l.split(":")}}
    
    @apicall
    @cache(3600)
    def search_account(self, email):
        """
        Search for leaked passwords for the given account.
        
        :param email: email address
        """
        self.__validate(email=email)
        return self._request(email)
