# -*- coding: UTF-8 -*-
"""Bot client dedicated to ZSIS CTF website.

This module provides a simple wrapper for conveniently writing solutions to the
 challenges of the "Programming" category.

"""
import re
from tinyscript.helpers.decorators import try_or_die

from ...core.protocols.http import HTTPBot
from ...core.utils.common import *


__all__ = ["ZSISBot"]

DOM = "ctf.zsis.hr"
URL = "https://{}/challenges/".format(DOM)
FLAG = re.compile(r'.*(FLAG\-\{.+\}).*')
CFN = ".cookie"


class ZSISBot(HTTPBot):
    """
    ZSISBot class implements an HTTP bot for solving challenges from the
     "Programming" category.

    :param cid:      challenge identifier
    :param cookie:   PHP session ID cookie
    :param args:     HTTPBot arguments
    :param kwargs:   HTTPBot keyword-arguments
    
    Note:
      The cookie can also be left None in the input arguments and be loaded from
       a .cookie file. It can be saved as "PHPSESSID=..." or simply "...".
    
    Example usage:
    
      from pybots import ZSISBot
      
      with ZSISBot("5_programming_some_challenge", "...your-cookie...") as bot:
          # do some computation with bot.inputs here
          # NOTE: bot.inputs is a dictionary containing input values from
          #        challenge's source ; i.e. 'challenge' for this particular bot
          bot.answer = computed_value
          # now, while exiting the context, the flag will be displayed if the
          #  answer was correct (or a message if wrong)
    """
    def __init__(self, cid, cookie, *args, **kwargs):
        if not cid.endswith(".php"):
            cid += ".php"
        super(ZSISBot, self).__init__("{}{}".format(URL, cid), *args, **kwargs)
        self.answer = None
        self.cid = cid
        # set the cookie
        if cookie is None:
            with open(CFN, 'r+') as f:
                cookie = f.read().strip()
        if not CKI.match(cookie):
            raise Exception
        if not cookie.startswith("PHPSESSID="):
            cookie = "PHPSESSID={}".format(cookie)
        self._set_cookie(cookie)

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
        self.inputs = {'challenge': self.response.text}

