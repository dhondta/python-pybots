# -*- coding: UTF-8 -*-
"""API client dedicated to DeHashed.

"""
from tinyscript.helpers.data.types import *

from ...core.utils.api import *


__all__ = ["DeHashedAPI"]


class DeHashedAPI(API):
    """
    Class for communicating with the API of DeHashed.
    
    Reference: https://www.dehashed.com/docs
    Note:      All API methods are rate-limited to 5 requests/250ms.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    url = "https://api.dehashed.com"
    
    def __init__(self, account, api_key, **kwargs):
        self.__validate(email=account)
        self.balance = None
        super(DeHashedAPI, self).__init__((account, api_key), **kwargs)
    
    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "domain":
                domain_name(v)
            elif k == "email":
                email_address(v)
            elif k == "page":
                positive_int(v, False)
    
    @time_throttle(.25, requests=5)
    def _request(self, query, **kwargs):
        """
        Generic post method.

        :param method:  HTTP method
        :param reqpath: request path
        :param kwargs:  requests.[...](...) parameters
        """
        kwargs['auth'] = self._api_key
        kwargs['params'] = kwargs.get('params', {})
        kwargs['params']['query'] = query
        super(DeHashedAPI, self)._request("/search", "get", **kwargs)
        if self._response.status_code == 400:
            raise APIError(self._json.get('Error 400'))
        elif self._response.text == "":
            raise APIError("No response")
        elif self._json.get('success'):
            self.balance = self._json.get('balance') or self.balance
            return self._json['entries']
        elif not self._json.get('success'):
            raise APIError(self._json.get('message'))
    
    @apicall
    @cache(300)
    def search(self, query, page=None):
        """
        Search for a given account in the remote database.
        
        :param email: email address
        :param page:  page number (5 results/page)
        """
        self.__validate(page=page, query=query)
        #FIXME: no query validation at this time ;
        # see https://www.dehashed.com/docs, section "Search Operators & Wildcard"
        params = {}
        if page:
            params = {'page': page}
        self._request(pattern, params=params)
    
    @apicall
    @cache(300)
    def search_account(self, email):
        """
        Search for a given account in the remote database.
        
        :param email: email address
        """
        self.__validate(email=email)
        self._request(email)
    
    @apicall
    @cache(300)
    def search_domain(self, domain, page=None):
        """
        Search for accounts matching the given domain.
        
        :param domain: domain name
        :param page:   page number (5 results/page)
        """
        self.__validate(domain=domain, page=page)
        params = {}
        if page:
            params = {'page': page}
        self._request(domain, params=params)

