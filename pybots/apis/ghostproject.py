# -*- coding: UTF-8 -*-
"""Bot client dedicated to Nuclear Leaks.

"""
import cloudscraper
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
        s['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        s['X-Requested-With'] = "XMLHttpRequest"
        try:
            cookies, uagent = cloudscraper.get_tokens(self.url + "/x000x1337.php")
        except Exception as e:
            if "Could not collect tokens" in str(e):
                raise APIError("Could not collect cloudflare clearance")
        self._session.cookies.update(cookies)
        self._session.headers['User-Agent'] = uagent

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
        super(GhostProjectAPI, self)._request("/x000x1337.php", "post", data={'param': query})
        if self._response.status_code != 200:
            raise APIError(self._response.reason)
        lines = self._response.text.strip("\r\n\"\\n").split("\\n")
        t = float(lines[0].split("Time: ")[1].split("<")[0])
        d = {}
        for l in lines[1:]:
            email, pswd = l.strip().split(":", 1)
            d.setdefault(email, [])
            d[email].append(pswd)
        return {'time': t, 'error': d['Error'][0].strip()} if 'Error' in d.keys() else {'time': t, 'data': d}

    @apicall
    @cache(3600)
    def search_account(self, email):
        """
        Search for leaked passwords for the given account.
        
        :param email: email address
        """
        self.__validate(email=email)
        return self._request(email)
