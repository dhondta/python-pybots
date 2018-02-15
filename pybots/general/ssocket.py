#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for socket communication.

This generic bot allows to manage a socket session by using simple read/write
 methods.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.3"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["SocketBot"]


import inspect
import os
import re
import socket
import sys
from six import string_types

from pybots.base.decorators import *
from pybots.base.template import Template


def addr_family(host):
    """
    Return the right address family (IPv4/IPv6) of host.

    :param host: input hostname or address
    :return:     the right socket address family
    """
    addr = socket.gethostbyname(host)
    try:
        socket.inet_pton(socket.AF_INET6, addr)
        return socket.AF_INET6
    except socket.error:
        return socket.AF_INET


class ProxySocket(object):
    """
    Proxy socket for tunneling socket communication through an HTTP tunnel.
    
    Inspired from implementation available at:
     http://code.activestate.com/recipes/577643-transparent-http-tunnel-for-
        python-sockets-to-be-u/

    :param sock:   socket instance
    :param phost:  proxy hostname or IP address
    :param pport:  proxy port number
    """
    def __init__(self, bot, sock, phost, pport):
        self.bot = bot
        self.bot.logger.debug("Setting up a ProxySocket...")
        self.socket = sock
        self.phost = phost
        self.pport = pport
        self.bot.logger.debug("Proxy: {}:{}".format(phost, pport))
        # bind every method of socket to self (except __init__ and connect,
        #  which are handled)
        bind = lambda i, f, n: setattr(i, n, f.__get__(i, i.__class__))
        for m, _ in inspect.getmembers(sock, predicate=inspect.ismethod):
            if m not in ["__init__", "connect"]:
                f = lambda s, *a, **kw: getattr(sock, m)(*a, **kw)
                bind(self, f, m)

    def connect(self, *args):
        """
        Create a tunnel through the proxy server.
        """
        self.bot.logger.debug("Connecting through the proxy...")
        # try to connect to the proxy
        pinfo = socket.getaddrinfo(self.phost, self.pport, 0, 0, socket.SOL_TCP)
        for family, stype, proto, _, addr in pinfo:
            try:
                # replace the socket by a connection to the proxy
                self.bot.socket = s = socket.socket_orig(family, stype, proto)
                s.connect(addr)
                break
            except socket.error as e:
                self.bot.close()
                raise e
        # create a tunnel connection to the target host/port
        self.socket.send("CONNECT {0}:{1} HTTP/1.1\r\nHost: {0}:{1}\r\n\r"
                         "\n".format(self.bot.host, self.bot.port));
        # get and parse the response
        resp = self.socket.recv(4096)
        error, resp = resp.split("\n", 1)
        status_code = int(error.split()[1])
        if status_code != 200:
            raise Exception("Proxy server returned error: {}".format(error))

    @staticmethod
    def setup(bot, phost, pport):
        def proxy_socket(*args, **kwargs):
            s = socket.socket_orig(*args, **kwargs)
            return ProxySocket(bot, s, phost, pport)
        socket.socket_orig = socket.socket
        socket.socket = proxy_socket


class SocketBot(Template):
    """
    Generic socket bot.
    
    Inspired from implementation available at:
     https://gist.github.com/leonjza/f35a7252babdf77c8421

    :param host:     hostname or IP address
    :param port:     port number
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    :param no_proxy: force ignoring the proxy
    """
    prefix_srv = "[SRV]"
    prefix_bot = "[BOT]"

    def __init__(self, host, port, disp=False, verbose=False, prefix=False,
                 no_proxy=False):
        super(SocketBot, self).__init__(verbose, no_proxy)
        self.__set_proxy()
        self.buffer = ""
        self.disp = disp
        self.host = host
        self.port = port
        self.prefix = prefix

    def __prefix_data(self, data, mode='r'):
        """
        Prefix data with bot/server mark if set through self.prefix.

        :param data: data to be prefixed
        :param mode: 'r' for read (from server), 'w' for write (from bot)
        :return:     data prefixed accordingly
        """
        if self.prefix:
            prefix = [self.prefix_bot, self.prefix_srv][mode == 'r']
            l = len(prefix)
            data = prefix + " " + "\n {0}".format(l * " ") \
                          .join(data.split('\n'))
        return data.strip()

    def __set_proxy(self):
        """
        Create specific socket object if a proxy is to be used.
        """
        try:
            prx = self._proxies['socks']
            phost, pport = prx.split("://")[1].split("/")[0].split(":")
            pport = int(pport)
        except KeyError:
            phost, pport = None, 0
        if phost is not None and pport in range(1, 2**16):
            ProxySocket.setup(self, phost, pport)
        elif hasattr(socket, "socket_orig"):  # reset original socket function
            socket.socket = socket.socket_orig
            delattr(socket, "socket_orig")

    def close(self):
        """
        Close the eventually opened socket.
        """
        try:
            self.socket.close()
            self.socket = None
        except:
            pass

    @try_or_die("Socket establishment failed", socket.error)
    def connect(self, host=None, port=None, timeout=0, blocking=True):
        """
        Create a socket and connect to the input host.

        :param host:     server hostname
        :param port:     port number
        :param timeout:  socket timeout
        :param blocking: set blocking socket
        """
        self.logger.debug("Connecting to the remote host...")
        restart = False
        if host is not None:  # new host was input through connect()
            self.host, restart = host, True
        if port is not None:  # new port was input through connect()
            self.port, restart = port, True
        if self.host and self.port:
            if restart:  # close and dispose the old socket
                self.close()
            # try to connect to the remote host
            i = socket.getaddrinfo(self.host, self.port, 0, 0, socket.SOL_TCP)
            for family, stype, proto, _, addr in i:
                self.socket = socket.socket(family, stype, proto)
                self.socket.connect(addr)
                break
            if self.socket is None:
                raise socket.error("Socket could not be established")
            # manage blocking and timeout
            if timeout > 0:
                self.socket.settimeout(timeout)
            self.socket.setblocking(blocking)
        else:
            self.logger.error("Missing parameter (host and/or port)")

    @try_or_die("Read failed")
    def read(self, length=1024, disp=None):
        """
        Read a given length of bytes off the socket.

        :param length: length of data to be read
        :param disp:   display the received data
        """
        self.logger.debug("Reading block of {}B...".format(length))
        data = ""
        try:
            data = self.socket.recv(length)
        except socket.error as e:
            self.logger.exception(str(e))
            self.close()
        except:
            self.close()
        if (self.disp if disp is None else disp) and len(data.strip()) > 0:
            print(self.__prefix_data(data, 'r'))
        return data
 
    def read_until(self, pattern, disp=None):
        """
        Read data into the buffer up to a given data.

        :param pattern: input pattern until which the data must be read
                        3 types are allowed:
                        - string
                        - list of strings
                        - compiled regex object (re.compile(...))
        :param disp:    display the received data
        """
        self.logger.debug("Reading until one of the given patterns...")
        if isinstance(pattern, string_types):
            pattern = [pattern]
        if isinstance(pattern, list):
            while not any(p in self.buffer for p in pattern):
                self.buffer += self.read(disp=disp)
            pattern = pattern[[p in self.buffer for p in pattern].index(True)]
        elif isinstance(pattern, type(re.compile(r''))):
            while not pattern.search(self.buffer):
                self.buffer += self.read(disp=disp)
            pattern = pattern.search(self.buffer).group()
        else:
            self.logger.error("Incorrect pattern")
            return
        p = pattern.encode('string-escape')
        self.logger.debug("Read until pattern '{}'".format(p))
        pos = self.buffer.find(pattern)
        data = self.buffer[:pos + len(pattern)]
        self.buffer = self.buffer[pos + len(pattern):]
        return data
  
    def receive(self, *a, **kw):
        """
        Alias for read and read_until.
        """
        return [self.read_until, self.read][isinstance(a[0], int) \
            if len(a) > 0 else 'pattern' not in kw.keys()](*a, **kw)

    def send(self, *a, **kw):
        """
        Alias for write.
        """
        return self.write(*a, **kw)
 
    def send_receive(self, data='', pattern='\n', eol='\n', disp=None):
        """
        Write input data to the socket and directly read until a given pattern.

        :param data:    input data to be sent
        :param pattern: input pattern until which the data must be read
        :param eol:     end of line characters
        :param disp:    display the sent data
        """
        self.write(data, eol, disp)
        return self.read_until(pattern, disp)

    @try_or_die("Write failed")
    def write(self, data='', eol='\n', disp=None):
        """
        Write input data to the socket.

        :param data: input data to be sent
        :param eol:  end of line characters
        :param disp: display the sent data
        """
        self.logger.debug("Writing to the socket...")
        try:
            self.socket.send(data + eol)
        except socket.error as e:
            self.logger.exception(str(e))
            self.close()
        except:
            return
        if (self.disp if disp is None else disp):
            print(self.__prefix_data(data, 'w'))
        return data
