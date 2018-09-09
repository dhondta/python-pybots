#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot clients dedicated to ZSIS CTF website.

This module provides a simple wrapper for conveniently writing solutions to the
 challenges of the "Programming" category.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["ZSISBot"]


import base64
import os
import re
import urllib

from pybots.base.decorators import *
from pybots.specific.http import HTTPBot


DOM = "ctf.zsis.hr"
URL = "https://{}/challenges/".format(DOM)
FLAG = re.compile(r'.*(FLAG\-\{.+\}).*')


class ZSISBot(HTTPBot):
    """
    ZSISBot class implements an HTTP bot for solving challenges from the
     "Programming" category.

    :param cid:      challenge identifier
    :param cookie: Root-Me username
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    """
    def __init__(self, cid, cookie, *args, **kwargs):
        if not cid.endswith(".php"):
            cid += ".php"
        super(ZSISBot, self).__init__("{}{}".format(URL, cid), *args, **kwargs)
        self._set_cookie("PHPSESSID={}".format(cookie))
        self.answer = None

    @try_or_die("Unexpected error")
    def postamble(self):
        """
        Custom postamble for submitting the answer and getting the flag.
        """
        self.flag = None
        if self.answer is None:
            self.flag = None
            self.logger.error("No answer provided")
            return
        self.get(params={'answer': self.answer})
        self.logger.debug(self.response.text)
        if "Wrong answer!" in self.response.text:
            self.logger.error("The answer is incorrect")
            return
        try:
            self.flag = FLAG.match(self.response.text).group(1)
            self.logger.info("Flag found: {}".format(self.flag))
        except AttributeError:
            self.logger.error("Could not retrieve the flag")

    @try_or_die("Could not retrieve challenge information")
    def preamble(self):
        """
        Custom preamble for getting the challenge information.
        """
        # get the challenge page and retrieve CSRF token and message
        self.get()
        self.logger.debug(self.response.text)
