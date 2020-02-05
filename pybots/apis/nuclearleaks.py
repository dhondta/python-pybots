# -*- coding: UTF-8 -*-
"""Bot client dedicated to Nuclear Leaks.

"""
import re
from tinyscript.helpers.data.types import *

from ..core.utils.api import *


__all__ = ["NuclearLeaksAPI"]


class NuclearLeaksAPI(API):
    """
    NuclearLeaksAPI class for communicating with the API of NuclearLeaks.
    
    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://nuclearleaks.com"
    
    def __init__(self, **kwargs):
        self.records = []
        kwargs['kind'] = "http"
        super(NuclearLeaksAPI, self).__init__(None, **kwargs)
    
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
        self.headers = [th.text for th in table.find('thead').findAll('th')]
        self.records = []
        for tr in table.find('tbody').findAll('tr'):
            row = []
            for td in tr.findAll('td'):
                row.append(td.text)
            self.records.append(row)
        return self.records
    
    def search(self, query):
        """
        Search for something in the Nuclear Leaks list.
        
        :param query: anything to be searched for in the list
        """
        self._request()
        r = []
        for row in self.records:
            for cell in row:
                if query in cell or re.search(query, cell):
                    r.append(dict(zip(self.headers, row)))
                    break
        return r
