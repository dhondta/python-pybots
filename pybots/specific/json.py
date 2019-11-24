# -*- coding: UTF-8 -*-
"""Bot client for HTTP session using JSON objects.

The JSONBot class, inheriting from the WebBot class holding the base mechanism
 and logging, manages Web interactions with the sites using JSON objects.

"""
import simplejson

from ..base.decorators import try_and_pass
from ..general.web import *


__all__ = ["JSONBot"]


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
    def __init__(self, *args, **kwargs):
        super(JSONBot, self).__init__(*args, **kwargs)
        self.session.headers.update({'Content-Type': "application/json"})

    @try_and_pass(simplejson.JSONDecodeError)
    def _parse(self):
        """
        Parse the requested JSON.
        """
        self.json = None  # this ensures that the json attribute is set
        self.json = simplejson.loads(self.response.text.strip())
