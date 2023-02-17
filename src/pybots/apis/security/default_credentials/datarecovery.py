# -*- coding: UTF-8 -*-
"""API client dedicated to DataRecovery.com.

"""
from ....core.utils.api import *


__all__ = ["DataRecoveryAPI"]


BAD_ENTRIES = []


class DataRecoveryAPI(SearchAPI):
    """
    Class for communicating with the website of DataRecovery.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://datarecovery.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(DataRecoveryAPI, self).__init__(None, **kwargs)
        self._request()
    
    @cache(86400)
    def _request(self):
        """
        DataRecovery list get method.
        """
        super(DataRecoveryAPI, self)._request("/rd/default-passwords", "get")
        if self._soup is None:
            raise APIError("bad URL")
        if self._response.status_code != 200:
            raise APIError("could not retrieve the list of DataRecovery")
        table = self._soup.find('div', attrs={'class': "table-responsive"}).find('table')
        self.headers = []
        self._API__bot.json = {'data': []}  # fake the result of a JSON bot
        for tr in table.find('tbody').findAll('tr'):
            row = {}
            if len(list(tr.findAll('td'))) == 0:
                if len(self.headers) > 0:
                    continue
                for th in tr.findAll('th'):
                    h = th.find('span').text.lower().replace("model/name", "name").replace("manufacturer", "vendor")
                    self.headers.append(h.strip())
            else:
                for i, td in enumerate(tr.findAll('td')):
                    try:
                        k, v = API._sanitize(self.headers[i], td.find('span').text)
                        row[k] = v
                    except AttributeError:
                        k, _ = API._sanitize(self.headers[i], "")
                        row[k] = ""
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
        Search for something in the DataRecovery list.
        
        :param query: anything to be searched for in the list
        """
        self._request()
        return super(DataRecoveryAPI, self)._search(query)
    
    @property
    def vendors(self):
        """
        List of vendors
        """
        self._request()
        return sorted(list(set(r['vendor'] for r in self._json['data'])))        

