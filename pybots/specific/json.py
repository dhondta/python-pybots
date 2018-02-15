#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for HTTP session using JSON objects.

The JSONBot class, inheriting from the WebBot class holding the base mechanism
 and logging, manages Web interactions with the sites using JSON objects.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["JSONBot"]


import simplejson

from pybots.base.decorators import try_and_pass
from pybots.general.web import *


class JSONBot(WebBot):
    """
    JSONBot class holding the machinery for building a JSON client.

    :param url:     base URL to the challenge site
    :param verbose: debug level
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots import JSONBot

      with JSONBot('http://127.0.0.1:8080') as bot:
          print(bot.get("/json").json)
          
    """
    def __init__(self, url, verbose=False, no_proxy=False):
        super(JSONBot, self).__init__(url, verbose, no_proxy)
        self.session.headers.update({'Content-Type': "application/json"})

    @try_and_pass(simplejson.JSONDecodeError)
    def _parse(self):
        """
        Parse the requested JSON.
        """
        self.json = simplejson.loads(self.response.text.strip())
