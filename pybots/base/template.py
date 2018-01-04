#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Generic bot client template.

Each specific bot inherits from the generic class "Template" holding the base
 machinery and logging for managing interactions with remote hosts.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.2"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["Template"]


import logging
import os
import signal
import sys

try:  # Python3
    from urllib.request import getproxies
except ImportError:  # Python2
    from urllib import getproxies

# colorize logging
try:
    import coloredlogs
    colored_logs_present = True
except ImportError:
    print("(Install 'coloredlogs' for colored logging)")
    colored_logs_present = False

from .decorators import *


LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%H:%M:%S'


class Template(object):
    """
    Template class holding the base machinery for building a bot.

    :param verbose:  verbose mode
    :param no_proxy: force ignoring the proxy
    """
    def __init__(self, verbose=False, no_proxy=False):
        # configure logging
        self.verbose = verbose
        self.configure()
        # execute precomputation if any
        self._precompute()
        # check for proxy configuration
        self._proxies = getproxies() if not no_proxy else {}
        for kenv in ['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY']:
            kdict = kenv.split('_')[0].lower()
            if kenv not in self._proxies and kenv in os.environ.keys():
                self._proxies.update({kdict: os.environ[kenv]})
        self.logger.debug("Base initialization done.")

    def __enter__(self):
        """
        Context manager enter method, executing after __init__.
        """
        self.logger.debug("Entering context...")
        self._preamble()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit method, for gracefully closing the bot.

        :param type:      type of exception that caused the context to be exited
        :param value:     value of exception
        :param traceback: traceback of exception
        """
        self.logger.debug("Exiting context...")
        self._postamble()
        if hasattr(self, "close"):
            self.logger.debug("Closing bot connection...")
            self.close()
        self._postcompute()
        self.logger.debug("Shutting down...")
        Template.shutdown()

    @try_or_die("Something failed during postamble.", extra_info=True)
    def _postamble(self):
        if hasattr(self, "postamble"):
            self.logger.debug("Executing postamble...")
            self.postamble()
            self.logger.debug("Postamble done.")

    @try_and_warn("Something failed during postcomputation.", extra_info=False)
    def _postcompute(self):
        if hasattr(self, "postcompute"):
            self.logger.debug("Postcomputing...")
            self.postcompute()
            self.logger.debug("Postcomputation done.")

    @try_or_die("Something failed during preamble.", extra_info=True)
    def _preamble(self):
        if hasattr(self, "preamble"):
            self.logger.debug("Executing preamble...")
            self.preamble()
            self.logger.debug("Preamble done.")

    @try_and_warn("Something failed during precomputation.", extra_info=False)
    def _precompute(self):
        if hasattr(self, "precompute"):
            self.logger.debug("Precomputing...")
            self.precompute()
            self.logger.debug("Precomputation done.")

    def configure(self, log_fmt=LOG_FORMAT, date_fmt=DATE_FORMAT):
        """
        Configure logging.

        :param log_fmt:  log message format
        :param date_fmt: datetime format
        """
        logging.basicConfig(format=log_fmt, datefmt=date_fmt,
                            level=[logging.INFO, logging.DEBUG][self.verbose])
        self.logger = logging.getLogger()
        self.logger.debug("Configuring logging...")
        if colored_logs_present:
            coloredlogs.DEFAULT_LOG_FORMAT = log_fmt
            coloredlogs.DEFAULT_DATE_FORMAT = date_fmt
            coloredlogs.install([logging.INFO, logging.DEBUG][self.verbose])

    @staticmethod
    def shutdown(signum=None, frame=None, code=0):
        """
        Exit handler.

        :param signal: signal number
        :param frame:  stack frame
        :param code:   exit code
        """
        logging.shutdown()
        try:
            __IPYTHON__
            quit(keep_kernel=True)
        except NameError:
            sys.exit(code)


# bind termination signal (Ctrl+C) to exit handler
signal.signal(signal.SIGINT, Template.shutdown)
