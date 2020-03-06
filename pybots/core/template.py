# -*- coding: UTF-8 -*-
"""Generic bot client template.

Each specific bot inherits from the generic class "Template" holding the base
 machinery and logging for managing interactions with remote hosts.

"""
import coloredlogs
import logging
import os
import sys
from io import StringIO
from tinyscript.helpers.decorators import *
try:  # Python3
    from urllib.request import getproxies
except ImportError:  # Python2
    from urllib import getproxies


__all__ = ["Template"]

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s %(message)s'
DATE_FORMAT = '%H:%M:%S'


class IpyExit(SystemExit):
    """Exit Exception for IPython.

    Exception temporarily redirects stderr to buffer.

    Source: https://stackoverflow.com/questions/44893461/problems-exiting-from-
             python-using-ipython-spyder/48000399#48000399
    """
    def __init__(self):
        sys.stderr = StringIO()

    def __del__(self):
        sys.stderr.close()
        sys.stderr = sys.__stderr__  # restore from backup


class Template(object):
    """
    Template class holding the base machinery for building a bot.

    :param verbose:  verbose mode
    :param no_proxy: force ignoring the proxy
    """
    bots = {}
    counters = {}

    def __init__(self, verbose=False, no_proxy=False):
        self._exited = False
        self.logger = None
        # keep track of bots
        c, t = self.__class__.__name__, Template
        t.bots.setdefault(c, {})
        t.counters.setdefault(c, 0)
        t.counters[c] += 1
        t.bots[c][self] = t.counters[c]
        self.name = "{}-{}".format(c, t.counters[c])
        # configure logging
        self.verbose = verbose
        self.configure()
        # configure post-execution workflow
        self.force_postamble = False    # (if exception raised)
        self.force_postcompute = False 
        # execute precomputation if any, before the connection is opened
        self._precompute()
        # check for proxy configuration
        if no_proxy:
            self._proxies = {}
        else:
            self._proxies = getproxies()
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

        :param exc_type:  type of exception that caused the context to be exited
        :param exc_value: value of exception
        :param traceback: traceback of exception
        """
        if self._exited:
            return
        self.__no_error = exc_type in (None, KeyboardInterrupt, SystemExit)
        if exc_type is KeyboardInterrupt:
            self.logger.warn("Bot execution interrupted.")
        self.logger.debug("Exiting context...")
        if self.__no_error or self.force_postamble:
            self._postamble()
        if hasattr(self, "close"):
            self.logger.debug("Gracefully closing bot...")
            self.close()
        # show the exception before attempting postcomputation
        if exc_type not in [KeyboardInterrupt, SystemExit] and \
           exc_value is not None:
            self.logger.exception(exc_value)
        # execute postcomputation if any, after the connection is closed
        if self.__no_error or self.force_postcompute:
            self._postcompute()
        # if run from IPython, handle exit without killing the current kernel
        try:
            __IPYTHON__
            quit(keep_kernel=True)
        except NameError:
            pass
        self._exited = True

    @try_or_die("Something failed during postamble.")
    def _postamble(self):
        if hasattr(self, "postamble"):
            self.logger.debug("Executing postamble...")
            self.postamble()
            self.logger.debug("Postamble done.")

    @try_and_warn("Something failed during postcomputation.")
    def _postcompute(self):
        if hasattr(self, "postcompute"):
            self.logger.debug("Postcomputing...")
            self.postcompute()
            self.logger.debug("Postcomputation done.")

    @try_or_die("Something failed during preamble.")
    def _preamble(self):
        if hasattr(self, "preamble"):
            self.logger.debug("Executing preamble...")
            self.preamble()
            self.logger.debug("Preamble done.")

    @try_and_warn("Something failed during precomputation.")
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
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_fmt, date_fmt)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel([logging.INFO, logging.DEBUG][self.verbose])
        coloredlogs.DEFAULT_LOG_FORMAT = log_fmt
        coloredlogs.DEFAULT_DATE_FORMAT = date_fmt
        coloredlogs.install([logging.INFO, logging.DEBUG][self.verbose],
                            logger=self.logger)
        self.logger.debug("Logging {}configured."
                          .format(["re", ""][self.logger is None]))
