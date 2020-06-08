# -*- coding: UTF-8 -*-
"""Bot clients dedicated to Root-Me CTF website.

This module currently contains an IRC bot for use with the challenges from the
 "Programming" category of Root-Me.

  NB: data is available through the attribute 'inputs' which is a dictionary
      whose keys are the tags found on the challenge page or a message given by
      an IRC bot

"""
from ...core.protocols.irc import IRCBot
from ...core.utils.common import *


__all__ = ["RootMeIRCBot"]


class RootMeIRCBot(IRCBot):
    """
    RootMeIRCBot class implements an IRC bot for solving challenges from the
     "Programming" category.

    :param cid:      challenge ID number
    :param username: Root-Me username
    
    Example usage:
    
      from pybots import RootMeIRCBot
      
      with RootMeIRCBot(1, "...your-rootme-username...") as bot:
          # do some computation with bot.inputs here
          # NOTE: bot.inputs is a dictionary containing input values from
          #        challenge's source ; i.e. 'message' for this particular bot
          bot.answer = computed_value
          # now, while exiting the context, the flag will be displayed if the
          #  answer was correct (or a message if wrong)        
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

