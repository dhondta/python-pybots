#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for EPassport remote virtual terminal.

This bot allows to communicate with an EPassport remote virtual terminal for
 reading passport information.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.1"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["EPassport"]


import re
import sys
try:
    from pypassport.apdu import CommandAPDU, ResponseAPDU
    from pypassport.epassport import EPassport as EPP
    from pypassport.reader import Reader
    pypassport_installed = True
except ImportError:
    pypassport_installed = False
    Reader = object

from .netcat import Netcat


def check_MRZ(method):
    """
    Method decorator for checking if the EPassport's MRZ is already set, that
     is, if set_MRZ(mrz) was already executed.

    :param method: EPassport object's method
    :return:       method wrapper
    """
    def _wrapper(self, *args, **kwargs):
        if hasattr(self, "mrz"):
            return method(self, *args, **kwargs)
        else:
            self.logger.warn("MRZ not set ; please use set_MRZ(mrz) method")
            dummy = lambda *a, **kw: None
            return dummy(self, *args, **kwargs)
    return _wrapper


class RemoteVirtualTerminal(Reader):
    """
    Socket virtual terminal for communicating with a remote server emulating an
     EPassport reader.

    :param bot: bot client to be bound to the terminal
    """
    readerNum = 0
    
    def __init__(self, bot):
        self.__bot = bot
        # convention: 0 is hexstring and 1 is raw bytes
        self.__in_fmt = None
        self.__out_fmt = None
    
    def __get_response(self, apdu):
        """
        This writes to the socket converting the string version of the APDU
         object (from pypassport) to something the remote server can understand.

        :param apdu: CommandAPDU object (see pypassport.apdu)
        """
        assert isinstance(apdu, CommandAPDU)
        self.__bot.logger.debug("--{}".format(str(apdu)))
        # this converts the string representation of CommandAPDU to an hexstring
        apdu = "".join(x.strip(">[]") for x in str(apdu).split())
        # when self.__mode is None, apdu is in hexstring format by default
        apdu = apdu.decode('hex') if self.__out_fmt == 1 else apdu
        response = self.__bot.send_receive(apdu).strip()
        cursor = [4, 2][self.__in_fmt == 1]
        response, code = response[:-cursor], response[-cursor:]
        shortened = (response[:37] + '...') if len(response) > 40 else response
        b = "{} [{}]".format(shortened, code).strip()
        self.__bot.logger.debug("<-- {}".format(b))
        return response, code

    def __set_format(self, response, code):
        """
        This sets the right format for ingoing APDU.

        :param response: APDU response
        :param code:     APDU code
        """
        if self.__in_fmt is None:
            try:
                int(response + code, 16)
                self.__in_fmt = 0
                # if the response is not 9000 (OK in hex string) then ingoing
                #  APDU format should be raw bytes
                if code != "9000":
                    self.__in_fmt = 1
                    print("wooops")
            except ValueError:
                self.__in_fmt = 1
            self.__bot.logger.debug("Ingoing APDU format determined as {}"
                .format(["hex string", "raw bytes"][self.__in_fmt]))
        if self.__out_fmt is None:
            # if the response was not OK (with any mode), then the ougoing APDU
            #  format was incorrect and is raw bytes
            self.__out_fmt = int(code != "9000" and code[-2:] != '\x90\x00')
            self.__bot.logger.debug("Outgoing APDU format determined as {}"
                .format(["hex string", "raw bytes"][self.__out_fmt]))
        
    def connect(self, readerNum=None):
        """
        Not required as this is handled in the bot.
        """
        pass
    
    def disconnect(self):
        """
        Not required as this is handled in the bot.
        """
        pass
    
    def getReaderList(self):
        """
        This returns the list of available readers, stating this class as the
         only available one.
        """
        return [self.__class__.__name__]
    
    def transmit(self, apdu):
        """
        Transmit an APDU object from pypassport through the socket and collect
         the response APDU from the remote server.

        :param apdu: CommandAPDU object
        """
        assert isinstance(apdu, CommandAPDU)
        response, code = self.__get_response(apdu)
        if self.__out_fmt is None or self.__in_fmt is None:
            self.__set_format(response, code)
            # now, retry with the correct formats
            response, code = self.__get_response(apdu)
        intcode = [int('0x{}'.format(h), 16) for h in re.findall('..', code)]
        return ResponseAPDU(response.decode('hex'), *intcode)


class EPassport(Netcat):
    """
    EPassport bot.

    :param host:     hostname or IP address
    :param port:     port number
    :param disp:     display all exchanged messages or not
    :param verbose:  verbose mode or not
    :param prefix:   prefix messages for display or not
    :param no_proxy: force ignoring the proxy

    Example usage:

      from pybots.epassport import EPassport

      with EPassport('127.0.0.1', 53121, disp=True, prefix=True) as passport:
          passport.set_MRZ("...").get_photo()
          
    """
    def __init__(self, *args, **kwargs):
        super(EPassport, self).__init__(*args, **kwargs)
        if not pypassport_installed:
            self.logger.critical("Cannot find pypassport !")
            self.logger.warn("Please install it manually (does not work with"
                             " Python 3)")
            sys.exit(1)

    def _terminal(self):
        """
        This instantiates the remote terminal to be used in self.set_MRZ(mrz).
         This can be overriden to handle another terminal class.
        """
        return RemoteVirtualTerminal(self)

    @check_MRZ
    def get_photo(self, filename="face.jpg"):
        """
        This retrieves the photo from the ePassport and saves it to a JPEG.

        :param filename: JPEG file name
        """
        self.logger.info("Get encoded face from DG2")
        with open(filename, 'wb') as f:
            f.write(self.epassport['DG2']['A1']['5F2E'])
        return self

    def set_MRZ(self, mrz):
        """
        This allows to set MRZ and to perform the Basic Access Control (BAC) as
         from the pypassport library.

        :param mrz: MRZ
        """
        self.mrz = mrz
        reader = self._terminal()
        self.logger.info("Select eMRTD Application")
        self.epassport = EPP(reader, mrz)
        self.logger.info("Basic Access Control")
        self.epassport.doBasicAccessControl()
        return self
