# -*- coding: UTF-8 -*-
"""API client dedicated to Censys.

"""
import re
from tinyscript.helpers.data.types import *

from ...core.utils.api import *


__all__ = ["CensysAPI"]


class CensysAPI(API):
    """
    Class for communicating with the API of Censys.
    
    Reference: https://censys.io/api
    Note:      All API methods are rate-limited to 1 request/second.

    :param api_id:     API id
    :param api_secret: API secret
    :param kwargs:     JSONBot / API keyword-arguments
    """
    url = "https://censys.io"
    
    def __init__(self, api_id, api_secret, **kwargs):
        super(CensysAPI, self).__init__((api_id, api_secret), **kwargs)
    
    def __validate(self, index, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        reg = {
            'fields': r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$",
            'query':  r"^[0-9a-z]+(\.[0-9a-z]+)*\:\s(.+)$",
            'result': r"^\d{4}(0[0-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])[A-Z]([0-1][0-9]|2[0-3])[0-5][0-9]$",
            'series': r"^[0-9a-z]+([-_][0-9a-z]+)*$",
        }
        if index not in ["ipv4", "websites", "certificates"]:
            raise ValueError("bad index")
        for k, v in kwargs.items():
            if k == "buckets":
                positive_int(v, False)
                if v > 500:
                    raise ValueError("value exceeding maximum allowed (500)")
            elif k == "domain":
                domain_name(v)
            elif k == "fields":
                for f in (v or []):
                    if not re.match(reg[k], f):
                        raise ValueError("bad field value (should be in dot notation)")
            elif k in ["flatten"]:
                if not isinstance(v, bool):
                    raise ValueError("bad boolean flag")
            elif k == "page":
                positive_int(v, False)
            elif k == "query":
                if not re.match(reg[k], v):
                    raise ValueError("bad query string")
            elif k == "result":
                if not re.match(reg[k], v):
                    raise ValueError("bad result ID")
            elif k == "series":
                if not re.match(reg[k], v):
                    raise ValueError("bad series ID")
    
    @time_throttle(1)
    def _request(self, method, reqpath, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param reqpath: request path
        :param kwargs:  requests.[...](...) parameters
        """
        kwargs['auth'] = self._api_key
        super(CensysAPI, self)._request("/api/v1" + reqpath, method, **kwargs)
    
    # Create Report endpoint: https://censys.io/api/v1/docs/report
    def _report(self, index, query, field=None, buckets=50):
        """
        The build report endpoint lets you run aggregate reports on the breakdown of a field in a result set analogous
         to the "Build Report" functionality in the front end. For example, if you wanted to determine the breakdown of
         cipher suites selected by Top Million Websites.
        
        :param query:   query to be executed, e.g. 80.http.get.headers.server: nginx
        :param field:   field to be run a breakdown on in dot notation, e.g. location.country_code
        :param buckets: maximum number of values to be returned in the report (max is 500)
        """
        self.__validate(index, query=query, fields=[field], buckets=buckets)
        data = {'query': query, 'buckets': buckets}
        if field:
            data['field'] = field
        self._request("post", "/report/%s" % index, json=data)
    
    # Search endpoint: https://censys.io/api/v1/docs/search
    def _search(self, index, query, page=1, fields=None, flatten=True):
        """
        Searches against the current data in the {0} index and returns a paginated result set of {0} that match the
         search.
        
        :param query:   query to be executed, e.g. 80.http.get.headers.server: nginx
        :param page:    page of the result set to be returned
                         NB:  The number of pages in the result set is available under metadata in any request.
        :param fields:  fields to be returned in the result set in dot notation, e.g. location.country_code
        :param flatten: format of the returned results
        """
        self.__validate(index, query=query, page=page, fields=fields, flatten=flatten)
        data = {'query': query, 'page': page, 'flatten': flatten}
        if fields:
            data['fields'] = fields
        self._request("post", "/search/%s" % index, json=data)
    
    # View Document endpoint: https://censys.io/api/v1/docs/view
    def _view(self, index, id):
        """
        Returns the current structured data we have on a specific {0}.
        
        :param id: ID of the requested document
        """
        self.__validate(index, id=id)
        self._request("get", "/view/%s/%s" % (index, id))
    
    # Account endpoint: https://censys.io/api/v1/docs/account
    @apicall
    @cache(300)
    def account(self):
        """
        Returns information about your Censys account.
        """
        self._request("get", "/account")
    
    # Get Series endpoint: https://censys.io/api/v1/docs/data
    @apicall
    @cache(300)
    def data(self):
        """
        Returns a data on the types of scans regularly performed ("series").
        """
        self._request("get", "/data")
    
    # View Series endpoint: https://censys.io/api/v1/docs/data
    @apicall
    @cache(300)
    def data_series(self, series):
        """
        Returns data about a particular series (a scan of the same protocol and destination accross time) including the
         list of scans.
        
        :param series: ID of the series, e.g., 22-ssh-banner-full_ipv4
        """
        self.__validate(series=series)
        self._request("get", "/data/%s" % series)
    
    # View Result endpoint: https://censys.io/api/v1/docs/data
    @apicall
    @cache(300)
    def data_series_result(self, series, result):
        """
        Returns data on a particular scan ("result"), as found in the Get Series or View Series endpoints.
        
        :param series: ID of the series, e.g., 22-ssh-banner-full_ipv4
        :param result: ID of the result, e.g., 20150930T0056
        """
        self.__validate(series=series, result=result)
        self._request("get", "/data/%s/%s" % (series, result))
    
    @apicall
    @cache(300)
    def report_certificates(self, query, page=1, fields=None, flatten=True):
        self._report("certificates", query, page, fields, flatten)
    report_certificates.__doc__ = _report.__doc__
    
    @apicall
    @cache(300)
    def report_ipv4(self, query, page=1, fields=None, flatten=True):
        self._report("ipv4", query, page, fields, flatten)
    report_ipv4.__doc__ = _report.__doc__
    
    @apicall
    @cache(300)
    def report_websites(self, query, page=1, fields=None, flatten=True):
        self._report("websites", query, page, fields, flatten)
    report_websites.__doc__ = _report.__doc__
    
    @apicall
    @cache(300)
    def search_certificates(self, query, page=1, fields=None, flatten=True):
        self._search("certificates", query, page, fields, flatten)
    search_certificates.__doc__ = _search.__doc__.format("certificates")
    
    @apicall
    @cache(300)
    def search_ipv4(self, query, page=1, fields=None, flatten=True):
        self._search("ipv4", query, page, fields, flatten)
    search_ipv4.__doc__ = _search.__doc__.format("ipv4")
    
    @apicall
    @cache(300)
    def search_websites(self, query, page=1, fields=None, flatten=True):
        self._search("websites", query, page, fields, flatten)
    search_websites.__doc__ = _search.__doc__.format("websites")
    
    @apicall
    @cache(300)
    def view_certificate(self, id):
        self._view("certificates", id)
    view_certificate.__doc__ = _view.__doc__.format("certificate")
    
    @apicall
    @cache(300)
    def view_ipv4(self, id):
        self._view("ipv4", id)
    view_ipv4.__doc__ = _view.__doc__.format("ipv4")
    
    @apicall
    @cache(300)
    def view_website(self, id):
        self._view("websites", id)
    view_website.__doc__ = _view.__doc__.format("website")

