# -*- coding: UTF-8 -*-
"""API client dedicated to NuclearLeaks.

"""
from datetime import datetime

from ...core.utils.api import *


__all__ = ["NuclearLeaksAPI"]


class NuclearLeaksAPI(SearchAPI):
    """
    Class for communicating with the API of NuclearLeaks.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://nuclearleaks.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(NuclearLeaksAPI, self).__init__(None, **kwargs)
        self._request()

    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
    
    @cache(86400)
    def _request(self):
        """
        Nuclear Leaks list get method.
        """
        super(NuclearLeaksAPI, self)._request("/", "get")
        if self._response.status_code != 200:
            raise APIError("could not retrieve the list of Nuclear Leaks")
        table = self._soup.find('table', id="breaches-table")
        self.headers = [th.text.lower().replace(" ", "_") for th in table.find('thead').findAll('th')]
        self._API__bot.json = {'data': []}
        for tr in table.find('tbody').findAll('tr'):
            row = {}
            for i, td in enumerate(tr.findAll('td')):
                k = self.headers[i].rstrip("?")
                row[k] = int(td.text.replace(",", "")) if k == "entries" else td.text
                if k == "dump_date":
                    t = td.text
                    row['year'] = int(t.split("-")[0]) if t != "" else datetime.now().year
            self._json['data'].append(row)
        return self._json
    
    @apicall
    def search(self, query):
        """
        Search for something in the Nuclear Leaks list.
        
        :param query: anything to be searched for in the list
        """
        self._request()
        return super(NuclearLeaksAPI, self)._search(query)

