# -*- coding: UTF-8 -*-
"""Bot client for HTTP session with response parsing.

The HTTPBot class, inheriting from the WebBot class holding the base mechanism and logging, manages Web interactions
 with the sites handling response parsing with BeautifulSoup. The JSONBot does the same, but handling a JSON request and
 response.

"""
import bs4
import simplejson
from tinyscript.helpers.decorators import *

from ..web import WebBot


__all__ = __features__ = ["HTTPBot", "JSONBot"]


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
    def parse(self):
        """
        Parse the requested Web page.
        """
        self.soup = None  # this ensures that the soup attribute is set
        self.soup = bs4.BeautifulSoup(self.response.text, 'html.parser')


class JSONBot(WebBot):
    """
    JSONBot class holding the machinery for building a JSON client.

    :param url:      base URL to the challenge site
    :param auth:     authentication credentials as a tuple
    :param verbose:  debug level
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots import JSONBot

      with JSONBot('http://127.0.0.1:8080') as bot:
          print(bot.get("/json").json)
          
    """
    json = None
    
    def __init__(self, *args, **kwargs):
        super(JSONBot, self).__init__(*args, **kwargs)
        self.json = None
        self.session.headers.update({'Content-Type': "application/json"})

    @try_and_pass(simplejson.JSONDecodeError)
    def parse(self):
        """
        Parse the requested JSON.
        """
        self.json = None  # this ensures that the json attribute is set
        self.json = simplejson.loads(self.response.text.strip())

