# -*- coding: UTF-8 -*-
"""API client tailored to the Google page sites.google.com/site/saynamweb/password.

"""
from ....core.utils.api import *


__all__ = ["SaynamWebAPI"]


BAD_ENTRIES = []


class SaynamWebAPI(SearchAPI):
    """
    Class for communicating with the Google page Saynam Web.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://sites.google.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(SaynamWebAPI, self).__init__(None, **kwargs)
        self._request()
    
    @cache(86400)
    def _request(self):
        """
        SaynamWebAPI list get method.
        """
        super(SaynamWebAPI, self)._request("/site/saynamweb/password", "get")
        if self._soup is None:
            raise APIError("bad URL")
        if self._response.status_code != 200:
            raise APIError("could not retrieve the list of SaynamWeb")
        table = self._soup.find('div', role="main").find('table').find('table')
        self.headers = []
        self._API__bot.json = {'data': []}  # fake the result of a JSON bot
        for i, tr in enumerate(table.find('tbody').findAll('tr')):
            row = {}
            for j, td in enumerate(tr.findAll('td')):
                if i == 0:
                    self.headers.append(td.text)
                else:
                    k, v = API._sanitize(self.headers[j], td.text)
                    if k == "access-type":
                        if v.lower() == "multi":
                            v = ""
                        v = list(filter(lambda x: x != "", map(lambda s: s.strip().lower(), v.split(","))))
                    elif k == "password":
                        m = re.match("\(any (\d+) characters\)", v)
                        if m:
                            n = m.group(1)
                            v = "*" * int(n)
                    row[k] = v
            if len(row) > 0:
                self._json['data'].append(row)
        return self._json
    
    @apicall
    def credentials(self, vendor):
        """
        Search for default credentials for a given vendor.
        
        :param vendor: vendor name
        """
        if vendor in BAD_ENTRIES:
            raise APIError("vendor '%s' is irrelevant" % vendor)
        self._request()
        return {'data': [{k: v for k, v in row.items() if k != "vendor"} for row in \
                         self._json['data'] if row['vendor'].lower() == vendor.lower()]}
    
    @apicall
    def search(self, query):
        """
        Search for something in the SaynamWebAPI list.
        
        :param query: anything to be searched for in the list
        """
        self._request()
        return super(SaynamWebAPI, self)._search(query)
    
    @property
    def vendors(self):
        """
        List of vendors
        """
        self._request()
        return sorted(list(set(r['vendor'] for r in self._json['data'])))        

