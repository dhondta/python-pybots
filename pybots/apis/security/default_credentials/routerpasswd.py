# -*- coding: UTF-8 -*-
"""API client dedicated to RouterPassword.com for searching for default credentials.

"""
from ....core.utils.api import *


__all__ = ["RouterPasswordsAPI"]


BAD_ENTRIES = []


class RouterPasswordsAPI(SearchAPI):
    """
    Class for communicating with the website of RouterPassword.com.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://www.routerpasswords.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(RouterPasswordsAPI, self).__init__(None, **kwargs)
    
    @cache(86400)
    def _request(self, vendor):
        """
        RouterPasswordsAPI list get method for a defined vendor.
        """
        if vendor in BAD_ENTRIES:
            raise APIError("vendor '%s' is irrelevant" % vendor)
        super(RouterPasswordsAPI, self)._request("/router-password/%s/" % urlencode(vendor), "get")
        if self._soup is None:
            raise APIError("bad URL")
        if self._response.status_code == 404:
            raise APIError("vendor '%s' does not exist" % vendor)
        self.headers = []
        self._API__bot.json = {'data': []}  # fake the result of a JSON bot
        for tr in self._soup.find('table', attrs={'class': "table"}).findAll('tr'):
            for th in tr.findAll('th'):
                self.headers.append(th.text)
            row = {}
            for k, td in zip(self.headers, tr.findAll('td')):
                k, v = API._sanitize(k, td.text)
                if k == "manufacturer":
                    continue
                elif k == "model":
                    k = "name"
                elif k == "protocol":
                    v = [] if v == "MULTI" else list(map(lambda s: s.strip().lower(), v.split(",")))
                row[k] = v
            if len(row) > 0:
                self._json['data'].append(row)
        return self._json
    
    @cache(86400)
    def _vendors(self):
        """
        RouterPasswordsAPI get method for the list of all vendors.
        """
        super(RouterPasswordsAPI, self)._request("/", "get")
        if self._soup is None:
            raise APIError("bad URL")
        return [o.text for o in self._soup.find('select', attrs={'name': "router"}).findAll('option', id="routerid")]
    
    @apicall
    def credentials(self, vendor):
        """
        Search for default credentials for a given vendor.
        
        :param vendor: vendor name
        """
        if vendor in BAD_ENTRIES:
            raise APIError("vendor '%s' is irrelevant" % vendor)
        return self._request(vendor)
    
    @apicall
    def search(self, query, vendor=None):
        """
        Search for something in the RouterPassword list.
        
        :param query: anything to be searched for in the list
        :param vendor: vendor name
        """
        data = {'data': []}
        for v in (self.vendors if vendor is None else [vendor]):
            try:
                r = self.credentials(v)
            except APIError:
                continue
            if vendor is None:
                r['vendor'] = v
            data['data'].append(r)
        self._json = data
        return super(RouterPasswordsAPI, self)._search(query)
    
    @property
    def vendors(self):
        """
        List of vendors
        """
        return self._vendors()

