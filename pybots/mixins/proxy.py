#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Mixins for selecting a public HTTP proxy.

This mixin allows to retrieve a proxy address from a public list of public HTTP
 proxies and to setup the bot with a selected one.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["PublicHTTPProxyMixin"]


from pybots.base.decorators import *
from pybots.utils.ip import find_public_http_proxy


@applicable_to("WebBot")
class PublicHTTPProxyMixin(object):
    @try_and_warn("Public HTTP proxy setting failed", trace=True)
    def set_public_proxy(self, country=None, source=None):
        """
        Setup a randomly chosen public HTTP proxy from available or one selected
         proxy list.

        For a list of supported proxy lists:

          >>> from pybots.utils.ip import get_public_http_proxies_sources
          >>> get_public_http_proxies_sources()

        :param country: origin country of the public proxy
        :param source:  network location of the source for public IP lookup
        """
        proxy = find_public_http_proxy(country, source, self.verbose)
        # NOTE: this supposes that the selected public proxy works ; retries not
        #        handled yet
        self._proxies.update({'http': proxy})
