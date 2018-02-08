#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for Web communication.

Each specific bot inherits from a generic Bot class holding the base
 mechanism and logging for managing Web interactions with the handled sites.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.5"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["WebBot"]


import copy
import logging
import os
import requests
import urllib3
from types import MethodType
try:  # Python3
    from urllib.request import urlretrieve
except ImportError:  # Python2
    from urllib import urlretrieve
try:  # Python3
    from urllib.parse import urljoin, urlparse
except ImportError:  # Python2
    from urlparse import urljoin, urlparse

from pybots.base.template import Template

# disable annoying requests warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.ERROR)
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


SUPPORTED_HTTP_METHODS = ["delete", "get", "head", "options", "post", "put"]


class WebBot(Template):
    """
    Bot template class holding the base machinery for building a Web bot.

    :param url:      base URL to the challenge site
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy
    """
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64;"
                             " rv:50.0) Gecko/20100101 Firefox/50.0",
               'Accept': "text/html,application/xhtml+xml,application/"
                         "xml;q=0.9,*/*;q=0.8",
               'Accept-Language': "en-US,en;q=0.5",
               'Accept-Encoding': "gzip, deflate, br",
               'Connection': "keep-alive",
               'DNT': "1", 'Upgrade-Insecure-Requests': "1"}

    def __init__(self, url, verbose=False, no_proxy=False):
        super(WebBot, self).__init__(verbose, no_proxy)
        parsed = urlparse(url)
        if parsed.scheme == '' or parsed.netloc == '':
            self.logger.error("Bad URL")
            self.shutdown()
        self.url = url + "/" if parsed.path == '' else url
        self.logger.debug("Creating a session...")
        self.session = requests.Session()
        self.logger.debug("Binding HTTP methods...")
        for m in SUPPORTED_HTTP_METHODS:
            setattr(WebBot, m, MethodType(WebBot.template(m), self))

    def __print_request(self):
        """
        Pretty print method for debugging HTTP communication.
        """
        data = "\n\n    {}\n".format(self._request.body) \
                if self._request.method == "POST" else "\n"
        self.logger.debug("Sent request:\n    {} {}\n{}".format( \
            self._request.method,
            self._request.url,
            '\n'.join('    {}: {}'.format(k, v) \
                for k, v in sorted(self._request.headers.items())))
            + data)

    def __print_response(self):
        """
        Pretty print method for debugging HTTP communication.
        """
        self.logger.debug("Received response:\n    {} {}\n{}\n"
            .format(self.response.status_code, self.response.reason,
            '\n'.join('    {}: {}'.format(k, v) \
                for k, v in sorted(self.response.headers.items()))))

    def _parse(self):
        """
        Template method for parsing the response.
        """
        pass

    def _set_cookie(self, cookie):
        """
        Simple method to add the cookie to the HTTP headers.

        :param cookie: content of the cookie
        """
        self.logger.debug("Setting the cookie...")
        self.headers.update({'Cookie': cookie})
        return self

    def request(self, reqpath="/", method="GET", data=None, addheaders=None):
        """
        Get a Web page.

        :param reqpath:    request path (to be added to self.url)
        :param method:     HTTP method
        :param data:       data to be sent (if applicable, i.e. for POST)
        :param addheaders: additional HTTP headers (dictionary)
        :post:             self.response, self.soup populated
        """
        self.logger.debug("Requesting with method {}...".format(method))
        url = urljoin(self.url, reqpath)
        headers = copy.deepcopy(self.headers)
        headers.update(addheaders or {})
        if not hasattr(requests, method.lower()):
            self.logger.error("Bad request")
            self.shutdown(1)
        self._request = requests.Request(method, url, data=data or {},
                                         headers=headers).prepare()
        self.__print_request()
        try:
            self.response = self.session.send(self._request,
                                              proxies=self._proxies,
                                              verify=False)
        except requests.exceptions.ProxyError:
            self.response = self.session.send(self._request, verify=False)
        self.__print_response()
        if self.response.status_code != 200:
            self.logger.error("Request failed")
            Bot.shutdown()
        self._parse()
        return self

    def retrieve(self, resource, filename=None):
        """
        Simple method for downloading a resource.

        :param resource: resource to be downloaded
        :param filename: destination filename
        """
        parsed = urlparse(resource)
        if filename is None:
            filename = os.path.basename(parsed.path) or "undefined"
        if parsed.netloc == '':
            resource = urljoin(self.url, resource)
        self.logger.debug("Downloading resource...")
        urlretrieve(resource, filename)
        self.logger.debug("> Saved to '{}'".format(filename))

    @staticmethod
    def template(method):
        """
        Template method for binding HTTP request methods to the WebBot.

        :param method: HTTP method to be bound
        """
        doc = """ Alias for request(method="{0}"). """
        if method in ["delete", "get", "head", "options"]:
            def f(self, reqpath="/", addheaders=None):
                return self.request(reqpath, method.upper(), None, addheaders)
        elif method in ["post", "put"]:
            def f(self, reqpath="/", data=None, addheaders=None):
                return self.request(reqpath, method.upper(), data, addheaders)
        f.__doc__ = doc.format(method.upper())
        return f
