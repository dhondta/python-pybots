# -*- coding: UTF-8 -*-
"""Bot client for HTTP session with response parsing.

The HTTPBot class, inheriting from the WebBot class holding the base mechanism
 and logging, manages Web interactions with the sites handling response parsing
 with BeautifulSoup.

"""
import bs4

from ..base.decorators import try_and_warn
from ..general.web import *


__all__ = ["HTTPBot"]


class HTTPBot(WebBot):
    """
    HTTPBot class holding the machinery for building an HTTP client.

    :param url:      base URL to the challenge site
    :param auth:     authentication credentials as a tuple
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots import HTTPBot

      with HTTPBot('http://127.0.0.1:8080') as bot:
          print(bot.get("/page.html").response.text)
          
    """
    soup = None
    
    @try_and_warn("BeautifulSoup parsing failed")
    def _parse(self):
        """
        Parse the requested Web page.
        """
        self.soup = bs4.BeautifulSoup(self.response.text, 'html.parser')
