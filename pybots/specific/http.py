#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for HTTP session with response parsing.

The HTTPBot class, inheriting from the WebBot class holding the base mechanism
 and logging, manages Web interactions with the sites handling response parsing
 with BeautifulSoup.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["HTTPBot"]


import bs4

from pybots.general.web import *


class HTTPBot(WebBot):
    """
    HTTPBot class holding the machinery for building an HTTP client.

    :param url:      base URL to the challenge site
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots import HTTPBot

      with HTTPBot('http://127.0.0.1:8080') as bot:
          print(bot.get("/page.html").response.text)
          
    """
    def _parse(self):
        """
        Parse the requested Web page.
        """
        self.soup = bs4.BeautifulSoup(self.response.text, 'html.parser')
