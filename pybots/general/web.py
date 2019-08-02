#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for Web communication.

Each specific bot inherits from a generic Bot class holding the base
 mechanism and logging for managing Web interactions with the handled sites.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.7"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["WebBot"]


import brotli
import copy
import logging
import os
import requests
import shutil
import urllib3
from types import MethodType
from user_agent import generate_user_agent
try:  # Python3
    from urllib.parse import urljoin, urlparse
except ImportError:  # Python2
    from urlparse import urljoin, urlparse

from pybots.base.decorators import *
from pybots.base.template import Template

# disable annoying requests warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.ERROR)
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


SUPPORTED_HTTP_METHODS = ["delete", "get", "head", "options", "post", "put"]


class DecompressedResponse(object):
    def __init__(self, response):
        self._response = response
    
    def __getattr__(self, name):
        return getattr(self._response, name)

    @property
    def text(self):
        """ Adapted from requests' Response object """
        content = None
        encoding = self._response.encoding
        if not self.content:
            return str('')
        if encoding is None:
            encoding = self._response.apparent_encoding
        try:
            content = str(self.content, encoding, errors='replace')
        except (LookupError, TypeError):
            content = str(self.content)
        return content


class WebBot(Template):
    """
    Bot template class holding the base machinery for building a Web bot.

    :param url:      base URL to the challenge site
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy
    """
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/60.0.3112.113 Safari/537.36",
               'Accept': "text/html,application/xhtml+xml,application/"
                         "xml;q=0.9,*/*;q=0.8",
               'Accept-Language': "en-US,en;q=0.5",
               'Accept-Encoding': "gzip, deflate, br",
               'Connection': "keep-alive",
               'DNT': "1", 'Upgrade-Insecure-Requests': "1"}

    def __init__(self, url, auth=None, verbose=False, no_proxy=False,
                 random_uagent=False):
        super(WebBot, self).__init__(verbose, no_proxy)
        self._parsed = urlparse(url)
        self.url = self._parsed.geturl()
        if self._parsed.scheme == '' or self._parsed.netloc == '':
            raise Exception("Bad URL")
        self.__auth = auth
        self.__ruagent = random_uagent
        self._set_session()
        self.logger.debug("Binding HTTP methods...")
        for m in SUPPORTED_HTTP_METHODS:
            setattr(self, m, MethodType(WebBot.template(m), self))

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
        self.__cookie = cookie
        self.session.headers.update({'Cookie': cookie})
        return self

    def _set_session(self):
        """
        Set a new session with the proxy to be used.
        """
        if hasattr(self, "session"):
            self.logger.debug("Resetting the session...")
        else:
            self.logger.debug("Creating a session...")
        self.session = requests.Session()
        if self.__auth:
            self.session.auth = self.__auth
        self.session.headers.update(self.headers)
        # instantiating the bot with random_uagent will randomize the user agent
        #  once per session
        if self.__ruagent:
            self.session.headers.update({'User-Agent': generate_user_agent()})
        self.session.proxies.update(self._proxies)

    def close(self):
        """
        Unset the eventually configured session.
        """
        try:
            self.session.close()
        except:
            pass
        self.session = None

    @property
    def cookie(self):
        """ Cookie property. """
        #FIXME: get the session cookie the right way...
        try:
            return self.session.headers.get("Cookie") or self.__cookie
        except AttributeError:
            return

    @cookie.setter
    def cookie(self, cookie):
        """ Cookie property setter. """
        # NOTE: _set_cookie is left for backward-compatibility
        if cookie is not None:
            self._set_cookie(cookie)

    @try_and_warn("Request failed")
    def request(self, rqpath=None, method="GET", data=None, aheaders=None, **kw):
        """
        Get a Web page.

        :param rqpath:   request path (to be added to self.url)
        :param method:   HTTP method
        :param data:     data to be sent (if applicable, i.e. for POST)
        :param aheaders: additional HTTP headers (dictionary)
        :post:           self.response, self.soup populated
        """
        assert type(data or {}) is dict
        assert type(aheaders or {}) is dict
        self.logger.debug("Requesting with method {}...".format(method))
        url = urljoin(self.url, rqpath)
        m = method.lower()
        if not hasattr(requests, m):
            self.logger.error("Bad request")
            raise AttributeError("requests has no method '{}'".format(m))
        session_params = {'allow_redirects': kw.pop('allow_redirects', True)}
        # handle request streaming (i.e. for downloads)
        stream = kw.pop('stream', None)
        if stream is not None:
            session_params['stream'] = stream
        # handle user agent randomization ; this allows to randomize the user
        #  agent at the request level and not the session one
        if kw.pop('random_uagent', False):
            aheaders = aheaders or {}
            aheaders['User-Agent'] = generate_user_agent()
        # now prepare the request
        request = requests.Request(method, url, data=data or {},
                                   headers=aheaders or {}, **kw)
        self._request = self.session.prepare_request(request)
        self.__print_request()
        # handle change in proxies configuration and send the request
        proxies = kw.pop('proxies', None)
        try:
            self.response = self.session.send(self._request,
                proxies=proxies or self.session.proxies, **session_params)
        except:
            self.response = self.session.send(self._request,
                proxies=proxies or self.session.proxies, verify=False,
                **session_params)
        self.__print_response()
        # handle HTTP status code here
        if 200 <= self.response.status_code < 300:
            # handle special encodings
            if self.response.headers.get('Content-Encoding') == "br":
                self.response = r = DecompressedResponse(self.response)
                try:
                    r.content = brotli.decompress(r.content)
                except Exception as e:
                    self.logger.exception(e)
            self._parse()
        return self

    @try_and_warn("Resource retrieval failed", trace=True)
    def retrieve(self, resource, filename=None):
        """
        Simple method for downloading a resource.

        :param resource: resource to be downloaded
        :param filename: destination filename
        """
        parsed, success = urlparse(resource), False
        if filename is None:
            filename = os.path.basename(parsed.path) or "undefined"
        if parsed.netloc == '':
            resource = urljoin(self.url, resource)
        self.logger.debug("Downloading resource...")
        with WebBot(resource, verbose=self.verbose) as bot:
            bot.cookie = self.cookie
            bot.get(resource, stream=True)
            if bot.response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in bot.response:
                        f.write(chunk)
                bot.logger.debug("> Download successful")
                self.logger.debug("> Saved to '{}'".format(filename))
                success = True
            else:
                bot.logger.error("> Download failed")
        if success:
            return filename

    @staticmethod
    def template(method):
        """
        Template method for binding HTTP request methods to the WebBot.

        :param method: HTTP method to be bound
        """
        doc = """ Alias for request(method="{0}"). """
        if method == "get":
            def f(self, rqpath=None, params=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), None, aheaders,
                                    params=params, **k)
        if method in ["delete", "head", "options"]:
            def f(self, rqpath=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), None, aheaders, **k)
        elif method in ["post", "put"]:
            def f(self, rqpath=None, data=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), data, aheaders, **k)
        f.__doc__ = doc.format(method.upper())
        return f
