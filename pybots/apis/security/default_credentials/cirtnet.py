# -*- coding: UTF-8 -*-
"""API client dedicated to CIRT.net for searching for default credentials.

"""
from ....core.utils.api import *


__all__ = ["CIRTnetAPI"]


BAD_ENTRIES = []


class CIRTnetAPI(SearchAPI):
    """
    Class for communicating with the website of CIRT.net.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://cirt.net"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(CIRTnetAPI, self).__init__(None, **kwargs)
    
    @cache(86400)
    def _request(self, vendor):
        """
        CIRTnetAPI list get method for a defined vendor.
        """
        vendor = re.sub(r"\s+, ", ", ", vendor)
        super(CIRTnetAPI, self)._request("/passwords?vendor=%s" % urlencode(vendor), "get")
        if self._soup is None:
            raise APIError("bad URL")
        if "Sorry, no matches" in self._soup.find('div', attrs={'class': "field-items"}).text:
            raise APIError("vendor '%s' does not exist" % vendor)
        self._API__bot.json = {'data': []}  # fake the result of a JSON bot
        for table in self._soup.find('div', attrs={'class': "field-items"}).findAll('table'):
            row = {}
            for tr in table.findAll('tr'):
                try:
                    k, v = list(tr.findAll('td'))
                    k, v = API._sanitize(k.find('b').text, v.text)
                    row[k] = v
                except ValueError:
                    pass
                try:
                    row['name'] = list(tr.findAll('td'))[0].find('i').text
                except AttributeError:
                    pass
            self._json['data'].append(row)
        return self._json
    
    @cache(86400)
    def _vendors(self):
        """
        CIRTnetAPI get method for the list of all vendors.
        """
        super(CIRTnetAPI, self)._request("/passwords", "get")
        if self._soup is None:
            raise APIError("bad URL")
        t = self._soup.find('div', attrs={'class': "field-items"}).find('table')
        return [a.text for a in t.findAll('a') if a.text != ""]
    
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
        Search for something in the CIRTnetAPI list.
        
        :param query: anything to be searched for in the list
        :param vendor: vendor name
        """
        data = {'data': []}
        for v in (self.vendors if vendor is None else [vendor]):
            r = self._request(v)
            if vendor is None:
                r['vendor'] = v
            data['data'].append(r)
        self._json = data
        return super(CIRTnetAPI, self)._search(query)
    
    @property
    def vendors(self):
        """
        List of vendors
        """
        return self._vendors()

