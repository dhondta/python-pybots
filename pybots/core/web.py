# -*- coding: UTF-8 -*-
"""Bot client for Web communication.

Each specific bot inherits from a generic Bot class holding the base
 mechanism and logging for managing Web interactions with the handled sites.

"""
import logging
import os
import requests
import urllib3
from six import string_types
from tinyscript.helpers.decorators import *
from types import MethodType
from user_agent import generate_user_agent

from .template import Template
from .utils.common import urljoin, urlparse

# disable annoying requests warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.ERROR)
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


__all__ = ["WebBot"]


class WebBot(Template):
    """
    Bot template class holding the base machinery for building a Web bot.

    :param url:      base URL to the challenge site
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy
    """
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/60.0.3112.113 Safari/537.36",
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               'Accept-Language': "en-US,en;q=0.5", 'Accept-Encoding': "gzip, deflate, br",
               'Connection': "keep-alive", 'DNT': "1", 'Upgrade-Insecure-Requests': "1"}

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
        for m in ["delete", "get", "head", "options", "post", "put"]:
            setattr(self, m, MethodType(WebBot.template(m), self))

    def __print_request(self):
        """
        Pretty print method for debugging HTTP communication.
        """
        headers = '\n'.join("    {}: {}".format(k, v) for k, v in sorted(self._request.headers.items()))
        data = "\n\n    {}\n".format(self._request.body) if self._request.method == "POST" else "\n"
        self.logger.debug("Sent request:\n    {} {}\n{}"
                          .format(self._request.method, self._request.url, headers + data))

    def __print_response(self):
        """
        Pretty print method for debugging HTTP communication.
        """
        headers = '\n'.join("    {}: {}".format(k, v) for k, v in sorted(self.response.headers.items()))
        self.logger.debug("Received response:\n    {} {}\n{}\n"
                          .format(self.response.status_code, self.response.reason, headers))

    def _set_cookie(self, cookie):
        """
        Simple method to add the cookie to the HTTP headers.

        :param cookie: content of the cookie
        """
        self.logger.debug("Setting the cookie...")
        self.__cookie = cookie
        self.session.headers.update({'Cookie': cookie})

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
        self.session.proxies.update(self.config.get('proxies', {}))

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
    
    @try_and_warn("Resource download failed", trace=True)
    def download(self, resource, filename=None):
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
        self.request(resource, stream=True)
        if self.response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in self.response:
                    f.write(chunk)
            self.logger.debug("> Download successful ; saved to '{}'".format(filename))
            success = True
        else:
            self.logger.error("> Download failed")
        if success:
            return filename
    retrieve = download

    @try_and_warn("Request failed", trace=True)
    def request(self, url=None, method="GET", data=None, aheaders=None, **kw):
        """
        Get a Web page.

        :param url:      full URL or request path (to be added to self.url)
        :param method:   HTTP method
        :param data:     data to be sent (if applicable, i.e. for POST)
        :param aheaders: additional HTTP headers (dictionary)
        :post:           self.response, self.soup populated
        """
        self.response = None
        aheaders = aheaders or {}
        data = data or {}
        if not isinstance(data, dict) and not isinstance(data, string_types):
            raise ValueError("Bad input data")
        if not isinstance(aheaders, dict):
            raise ValueError("Bad input additional headers")
        self.logger.debug("Requesting with method {}...".format(method))
        url = self.url if url is None else urljoin(self.url, url)
        m = method.lower()
        if not hasattr(requests, m):
            self.logger.error("Bad request")
            raise AttributeError("requests has no method '{}'".format(m))
        session_params = {'allow_redirects': kw.pop('allow_redirects', True)}
        # handle request streaming (i.e. for downloads)
        session_params['stream'] = kw.pop('stream', False)
        # handle user agent randomization ; this allows to randomize the user agent at the request level and not the
        #  session one
        if kw.pop('random_uagent', False):
            aheaders['User-Agent'] = generate_user_agent()
        # now prepare the request
        request = requests.Request(method, url, data=data or {}, headers=aheaders or {}, **kw)
        self._request = self.session.prepare_request(request)
        self.__print_request()
        # handle change in proxies configuration and send the request
        session_params['proxies'] = kw.pop('proxies', None) or self.session.proxies
        try:
            self.response = self.session.send(self._request, **session_params)
        except:
            session_params['verify'] = False
            self.response = self.session.send(self._request, **session_params)
            self.logger.debug("HTTPS certificate NOT verified")
        self.__print_response()
        if hasattr(self, "parse"):
            self.logger.debug("Parsing response...")
            self.parse()
            self.logger.debug("Parsing done.")
        return self

    @staticmethod
    def template(method):
        """
        Template method for binding HTTP request methods to the WebBot.

        :param method: HTTP method to be bound
        """
        doc = """ Alias for request(method="{0}"). """
        if method == "get":
            def f(self, rqpath=None, params=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), None, aheaders, params=params, **k)
        if method in ["delete", "head", "options"]:
            def f(self, rqpath=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), None, aheaders, **k)
        elif method in ["post", "put"]:
            def f(self, rqpath=None, data=None, aheaders=None, **k):
                return self.request(rqpath, method.upper(), data, aheaders, **k)
        f.__doc__ = doc.format(method.upper())
        return f

