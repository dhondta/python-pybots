# -*- coding: UTF-8 -*-
"""Bot client for IRC sessions.

This bot allows to manage Internet Chat Relay discussion.

"""
from ..ssocket import SocketBot


__all__ = __features__ = ["IRCBot"]


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

      from pybots import IRCBot

      with IRCBot('127.0.0.1', channel="test") as bot:
          bot.msg("world", "Hello !")
    """
    def __init__(self, host, port=6667, channel=None, nickname="ircbot", fullname="IRC Bot", *args, **kwargs):
        super(IRCBot, self).__init__(host, port, *args, **kwargs)
        if channel and not channel.startswith("#"):
            channel = "#" + channel
        self.channel = channel
        self.nickname = nickname
        self.fullname = fullname
        self.connect()
        self.write("NICK {}".format(nickname))
        self.write("USER {} * * :{}".format(nickname, fullname))
        self.msg("nickserv", "iNOOPE")
        self.join(channel)

    def close(self, exit=True):
        """
        Close the IRC session.
        """
        self.write("QUIT :End of session")
        super(IRCBot, self).close(exit)

    def join(self, channel=None):
        """
        Join an IRC channel (if any provided).
        """
        channel = channel or self.channel
        if channel is not None:
            if not channel.startswith("#"):
                channel = "#" + channel
            self.logger.debug("Joining channel {}...".format(channel))
            self.channel = channel
            self.write("JOIN {}".format(channel))
            self.logger.debug("Handling PING if any...")
            self.buffer = self.read()
            if "PING " in self.buffer:
                pong = self.buffer.split("PING ")[1].strip()
                self.write("PING {}".format(pong), eol="\r\n")  
                self.buffer = self.read()

    def msg(self, dest, msg):
        """
        Method for sending private messages.
        """
        self.write("PRIVMSG {} :{}".format(dest, msg), eol="\r\n")

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

