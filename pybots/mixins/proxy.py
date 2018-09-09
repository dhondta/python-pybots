#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Mixins for selecting a public HTTP proxy.

This mixin allows to retrieve a proxy address from a public list of public HTTP
 proxies and to setup the bot with a selected one.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.1"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["PublicHTTPProxyMixin", "PublicSocksProxyMixin"]


from pybots.base.decorators import *
from pybots.utils.ip import get_my_public_ip
from pybots.utils.proxy import *


@applicable_to("WebBot")
class PublicHTTPProxyMixin(object):
    @try_and_warn("Public HTTP proxy setting failed", trace=True)
    def set_public_proxy(self, proxy=None, country=None, netloc=None):
        """
        Setup a randomly chosen public HTTP proxy from available proxy list or
         a single one selected by country or network location.

        For a list of supported proxy lists:

          >>> from pybots.utils.proxy import get_public_http_proxies_sources
          >>> get_public_http_proxies_sources()

        :param proxy:   public proxy address
        :param country: origin country of the public proxy
        :param netloc:  network location of the source for public IP lookup
        """
        if proxy is None:
            proxy = find_public_http_proxy(country, netloc, self.verbose)
        # NOTE: this supposes that the selected public proxy works ; retries not
        #        handled yet
        self._old_public_ip = get_my_public_ip()
        self._proxies.update({'http': proxy})
        self._set_session()


@applicable_to("SocketBot")
class PublicSocksProxyMixin(object):
    @try_and_warn("Public Socks proxy setting failed", trace=True)
    def set_public_proxy(self, country=None, source=None):
        """
        Setup a randomly chosen public Socks proxy from available proxy list or
         a single one selected by country or network location.

        For a list of supported proxy lists:

          >>> from pybots.utils.proxy import get_public_socks_proxies_sources
          >>> get_public_socks_proxies_sources()

        :param country: origin country of the public proxy
        :param netloc:  network location of the source for public IP lookup
        """
        proxy = find_public_socks_proxy(country, netloc, self.verbose)
        # NOTE: this supposes that the selected public proxy works ; retries not
        #        handled yet
        self._proxies.update({'socks': proxy})
        self._set_session()
