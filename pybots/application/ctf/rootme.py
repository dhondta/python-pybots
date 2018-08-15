#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot clients dedicated to Root-Me CTF website.

This module currently contains an IRC bot for use with the challenges from the
 "Programming" category of Root-Me.

  NB: data is available through the attribute 'inputs' which is a dictionary
      whose keys are the tags found on the challenge page or a message given by
      an IRC bot

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.2"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["RootMeIRCBot"]


import base64
import os
import re
from six import string_types

from pybots.specific.irc import IRCBot


class RootMeIRCBot(IRCBot):
    """
    RootMeIRCBot class implements an IRC bot for solving challenges from the
     "Programming" category.

    :param cid:      challenge ID number
    :param username: Root-Me username
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    """
    def __init__(self, cid, username, *args, **kwargs):
        super(RootMeIRCBot, self).__init__("irc.root-me.org",
            channel="#root-me_challenge", nickname=username, *args, **kwargs)
        self.answer = None
        self.cid = int(cid)

    def postamble(self):
        """
        Custom postamble for submitting the answer and getting the flag.
        """
        self.msg("candy", "!ep{} -rep {}".format(self.cid, self.answer))
        self.read_until("You dit it! You can validate the challenge with the"
                        " password")
        self.flag = self.buffer.strip()
        self.logger.info(self.flag)

    def preamble(self):
        """
        Custom preamble method for initiating the challenge.
        """
        pattern = "MODE {} +x".format(self.nickname)
        if pattern not in self.buffer:
            self.read_until(pattern)
        self.msg("candy", "!ep{}".format(self.cid))
        self.read_until("PRIVMSG {} :".format(self.nickname))
        self.inputs = {'message': self.buffer.strip()}
