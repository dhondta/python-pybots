#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for TCP sessions.

This bot allows to manage a TCP session by using simple read/write methods.

A series of read/write operations or a complete session can be written in the
 preamble() method.

If necessary, data can be precomputed in a precompute() method in order to have
 it available for handling (e.g. a lookup table).

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.3"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["Netcat", "TCPBot"]


from pybots.general.ssocket import SocketBot


class TCPBot(SocketBot):
    """
    TCP session bot.

    :param host:     hostname or IP address
    :param port:     port number
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots.tcp import TCPBot

      class MyTCPBot(TCPBot):
          def preamble(self):
              self.read_until('>')
              self.write('hello')
              self.read_until('>')

      with MyTCPBot('127.0.0.1', 53121) as tcp:
          tcp.write('set')
          tcp.read_until('id:')
    """
    def __init__(self, *args, **kwargs):
        super(TCPBot, self).__init__(*args, **kwargs)
        self.connect()

    def preamble(self):
        """
        Default preamble to be processed during a session.
        """
        self.read_until('\n', disp=True)


class Netcat(TCPBot):
    """
    Kept for backward-compatibility.
    """
    pass
