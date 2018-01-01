#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for IRC sessions.

This bot allows to manage Internet Chat Relay discussion.

If necessary, data can be precomputed in a precompute() method in order to have
 it available for handling (e.g. a lookup table).

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["IRCBot"]


from .ssocket import SocketBot


class IRCBot(SocketBot):
    """
    Internet Relay Chat bot.

    :param host:     hostname or IP address
    :param port:     port number
    :param channel:  IRC channel
    :param nickname: bot's nickname
    :param fullname: bot's fullname
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots.irc import IRCBot

      class MyIRCBot(IRCBot):
          def preamble(self):
              self.msg("helloserv", "Hello!")

      with MyIRCBot('127.0.0.1', channel="#test-channel", disp=True) as bot:
          bot.msg("world", "Hello !")
          bot.read_until("Hello")
    """
    def __init__(self, host, port=6667, channel=None, nickname="ircbot",
                 fullname="IRC Bot", *args, **kwargs):
        super(IRCBot, self).__init__(host, port, *args, **kwargs)
        self.channel = channel
        self.nickname = nickname
        self.fullname = fullname
        # after that, initialize the connection
        self.connect()
        # handle preamble
        self.write("NICK {}".format(nickname))
        self.write("USER {} * * :{}".format(nickname, fullname))
        self._preamble()
        if channel is not None:
            self.write("JOIN {}".format(channel))
    
    def close(self, exit=True):
        """
        Close the IRC session.
        """
        self.write("QUIT :End of session")
        super(IRCBot, self).close(exit)

    def msg(self, dest, msg):
        """
        Method for sending private messages.
        """
        self.write("PRIVMSG {} :{}".format(dest, msg), eol="\r\n")

    def preamble(self):
        """
        Default preamble to be processed during a session.
        """
        pass

    def read(self, length=1024, disp=None):
        """
        Read a given length of bytes and check for errors.

        :param length: length of data to be read
        :param disp:   display the received data
        """
        data = super(IRCBot, self).read(length, disp)
        if "ERROR" in data:
            self.logger.error(data.strip())
            self.close()
        return data
