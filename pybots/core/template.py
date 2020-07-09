# -*- coding: UTF-8 -*-
"""Generic bot client template.

Each specific bot inherits from the generic class "Template" holding the base machinery and logging for managing
 interactions with remote hosts.

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

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
DATE_FORMAT = "%H:%M:%S"


class IpyExit(SystemExit):
    """Exit Exception for IPython.

    Exception temporarily redirects stderr to buffer.

    Source: https://stackoverflow.com/questions/44893461/problems-exiting-from-python-using-ipython-spyder/48000399
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
        self.config = {}
        self.logger = None
        # keep track of bots
        c, t = self.__class__.__name__, Template
        t.bots.setdefault(c, {})
        t.counters.setdefault(c, 0)
        t.counters[c] += 1
        t.bots[c][self] = t.counters[c]
        self.name = "{}-{}".format(c, t.counters[c])
        # configure logging
        self._set_logging(verbose=verbose)
        # execute precomputation if any, before the connection is opened
        self.__precompute()
        # check for proxy configuration
        if not no_proxy:
            proxies = getproxies()
            for k, v in proxies.items():
                self._set_option('proxies', k, v)
            for kenv in ['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY']:
                if kenv in os.environ.keys():
                    self._set_option('proxies', kenv.split('_')[0].lower(), os.environ[kenv])
        self.logger.debug("Base initialization done.")
    
    def __enter__(self):
        """
        Context manager enter method, executing after __init__.
        """
        self.logger.debug("Entering context...")
        self.__preamble()
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
        if self.__no_error or self._get_option('bot', 'force_postamble', False):
            self.__postamble()
        if hasattr(self, "close"):
            self.logger.debug("Gracefully closing bot...")
            self.close()
        # show the exception before attempting postcomputation
        if exc_type not in [KeyboardInterrupt, SystemExit] and exc_value is not None:
            self.logger.exception(exc_value)
        # execute postcomputation if any, after the connection is closed
        if self.__no_error or self._get_option('bot', 'force_postcompute', False):
            self.__postcompute()
        # if run from IPython, handle exit without killing the current kernel
        try:
            __IPYTHON__
            quit(keep_kernel=True)
        except NameError:
            pass
        self._exited = True
    
    def __getitem__(self, key):
        """
        Get a section or an option value of the configuration dictionary using the `object['key']` syntax.

        :param key: configuration section or 2-tuple with the configuration section and the option name
        """
        return self._get_option(*key) if isinstance(key, tuple) else self.config.get(key, {})
    
    def __setitem__(self, key, value):
        """
        Set an option value of the configuration dictionary using the `object['key']` syntax.

        :param key:   2-tuple with the configuration section and the option name
        :param value: option value
        """
        try:
            section, option = key
            self._set_option(section, option, value)
        except ValueError:
            self.logger.error("Bad config key ; should be a 2-tuple with the configuration section and option names")
    
    @try_or_die("Something failed during postamble.")
    def __postamble(self):
        if hasattr(self, "postamble"):
            self.logger.debug("Executing postamble...")
            self.postamble()
            self.logger.debug("Postamble done.")
    
    @try_and_warn("Something failed during postcomputation.")
    def __postcompute(self):
        if hasattr(self, "postcompute"):
            self.logger.debug("Postcomputing...")
            self.postcompute()
            self.logger.debug("Postcomputation done.")
    
    @try_or_die("Something failed during preamble.")
    def __preamble(self):
        if hasattr(self, "preamble"):
            self.logger.debug("Executing preamble...")
            self.preamble()
            self.logger.debug("Preamble done.")
    
    @try_and_warn("Something failed during precomputation.")
    def __precompute(self):
        if hasattr(self, "precompute"):
            self.logger.debug("Precomputing...")
            self.precompute()
            self.logger.debug("Precomputation done.")
    
    def _get_option(self, section, option, default=None, options=None):
        """
        Get (and set if relevant) an option value from the configuration dictionary, given an input dictionary of
         options if defined (typically the keyword-arguments from a method). It sets the value in the following order of
         precedence: (1) 'options' argument, (2) current config then (3) 'default' argument.
        
        :param section: configuration section
        :param option:  option name
        :param default: default value
        :param options: keyword-arguments dictionary
        """
        self.config.setdefault(section, {})
        default = self.config[section].get(option, default)
        self.config[section][option] = v = (options or {}).get(option, default)
        if self.logger:
            self.logger.debug("Config[{}][{}] = {}".format(section, option, v))
        return v
    
    def _set_logging(self, **kwargs):
        """
        Configure logging.

        :param log_fmt:  log message format
        :param date_fmt: datetime format
        """
        log_fmt = self._get_option('logging', 'log_format', LOG_FORMAT, kwargs)
        date_fmt = self._get_option('logging', 'date_format', DATE_FORMAT, kwargs)
        verbose = self._get_option('logging', 'verbose', False, kwargs)
        first = self.logger is None
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_fmt, date_fmt)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel([logging.INFO, logging.DEBUG][verbose])
        coloredlogs.DEFAULT_LOG_FORMAT = log_fmt
        coloredlogs.DEFAULT_DATE_FORMAT = date_fmt
        coloredlogs.install([logging.INFO, logging.DEBUG][verbose], logger=self.logger)
        self.logger.debug("Logging {}configured.".format(["re", ""][first]))
    
    def _set_option(self, section, option, value):
        """
        Set an option value of the configuration dictionary.
        
        :param section: configuration section
        :param option:  option name
        :param value:   option value
        """
        self.config.setdefault(section, {})
        self.config[section][option] = value

