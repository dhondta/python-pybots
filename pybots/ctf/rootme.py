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
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["RootMeIRCBot"]


import base64
import os
import re
from six import string_types

from pybots.irc import IRCBot


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
    def __init__(self, cid, username, disp=False, verbose=False, prefix=True):
        self.cid = int(cid)
        # initialize the bot
        super(RootMeIRCBot, self).__init__("irc.root-me.org",
            channel="#root-me_challenge", nickname=username, disp=disp,
            prefix=prefix, verbose=verbose)
        # start communication with RootMe's IRC server
        self.read_until("MODE {} +x".format(self.nickname))
        self.msg("candy", "!ep{}".format(self.cid))
        self.read_until("PRIVMSG {} :".format(self.nickname))
        self.inputs = {'message': self.buffer.strip()}
        self.buffer = ""
        self.answer = None

    def __exit__(self, *args, **kwargs):
        """
        Exit method for answering to the server and getting the flag.
        """
        self.msg("candy", "!ep{} -rep {}".format(self.cid, self.answer))
        self.read_until("You dit it! You can validate the challenge with the"
                        " password")
        self.flag = self.buffer.strip()
        self.logger.info(self.flag)
        self.buffer = ""
        super(RootMeIRCBot, self).__exit__(*args, **kwargs)

    def preamble(self):
        """
        Preamble method for contacting RootMe IRC server.
        """
        self.msg("nickserv", "iNOOPE")
