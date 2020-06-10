# -*- coding: UTF-8 -*-
"""API client dedicated to GhostProject.

"""
from tinyscript.helpers.data.types import *

from ...core.utils.api import *
from ...core.utils.cloudflare import get_clearance


__all__ = ["GhostProjectAPI"]


class GhostProjectAPI(API):
    """
    Class for communicating with the API of GhostProject.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    url = "https://ghostproject.fr"
    no_error = ["No results found"]
    
    def __init__(self, **kwargs):
        driver = kwargs.pop('driver', "firefox")
        timeout = kwargs.pop('clearance_timeout', 60)
        kwargs['random_uagent'] = False
        super(GhostProjectAPI, self).__init__(None, **kwargs)
        cookies, uagent = get_clearance(self.url, driver=driver, timeout=timeout)
        for cookie in cookies:
            self._session.cookies.set(**cookie)
        s = self._session.headers
        s['Cache-Control'] = "no-cache"
        s['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        s['Origin'] = self.url
        s['Pragma'] = "no-cache"
        s['TE'] = "Trailers"
        s['X-Requested-With'] = "XMLHttpRequest"
        s['User-Agent'] = uagent

    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "email":
                email_address(v)
    
    @time_throttle(2.5, 5)
    def _request(self, query):
        """
        Generic post method.
        
        :param query: query string (email or domain with wildcard)
        """
        super(GhostProjectAPI, self)._request("/x000x1337.php", "post", data={'param': query})
        if self._response.status_code != 200:
            raise APIError(self._response.reason)
        lines = self._response.text.strip("\r\n\"\\n").split("\\n")
        try:
            t = float(lines[0].split("Time: ")[1].split("<")[0])
        except IndexError:
            return {'error': "\n".join(lines)}
        d = {}
        for l in lines[1:]:
            email, pswd = l.strip().split(":", 1)
            d.setdefault(email, [])
            d[email].append(pswd)
        if 'Error' in d.keys():
            err = d['Error'][0].strip()
            if err == "No results found":
                return {'time': t, 'data': {}}
            return {'time': t, 'error': err}
        return {'time': t, 'data': d}

    @apicall
    @cache(3600)
    def search(self, email):
        """
        Search for leaked passwords for the given account.
        
        :param email: email address
        """
        self.__validate(email=email)
        return self._request(email)

