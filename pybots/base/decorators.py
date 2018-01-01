#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Decorators for bot methods.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["try_or_die", "try_and_warn", "try_inputs"]


import logging
import sys
from io import StringIO


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


def __shutdown(instance, code):
    """
    Shutdown function for calling instance's close method if exists, then using
     template class' shutdown method.

    :param self: bot instance
    :param code: error code
    """
    if hasattr(instance, "close"):
        instance.close()
    logging.shutdown()
    try:
        __IPYTHON__
        quit(keep_kernel=True)
    except NameError:
        sys.exit(code)


def try_or_die(message, exc=Exception, code=1, extra_info=None):
    """
    Decorator handling a try-except block to log an error and gracefully
     shutdown the bot.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param code:       exit code
    :param extra_info: class attribute value to be displayed as additional
                        information
    """
    def _try_or_die(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                self.logger.critical(message)
                if extra_info is not None:
                    self.logger.exception(exc)
                    if hasattr(self, str(extra_info)):
                        self.logger.debug(getattr(self, extra_info))
                __shutdown(self, code)
        return wrapper
    return _try_or_die


def try_and_warn(message, exc=(AttributeError, IndexError), code=1,
                 extra_info=None):
    """
    Decorator handling a try-except block to log a warning and continue
     the execution of the bot.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param code:       exit code
    :param extra_info: class attribute value to be displayed as additional
                        information
    """
    def _try_and_warn(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                self.logger.warn(message)
                if extra_info is not None:
                    self.logger.exception(exc)
                    if hasattr(self, str(extra_info)):
                        self.logger.debug(getattr(self, extra_info))
        return wrapper
    return _try_and_warn


def try_inputs(message, exc=(AttributeError, KeyError), code=1):
    """
    Decorator handling a try-except block catching the key errors while
     trying to use a non-existing key in self.inputs dictionary.

    :param message: message to be displayed when crashing
    :param exc:     exception class on which the error is thrown
    :param code:    exit code
    """
    def _try_inputs(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                if hasattr(self, "inputs"):
                    self.logger.debug("Available input keys:\n{}".format(
                        '\n'.join([" - {}: {}".format(k, v) \
                         for k, v in self.inputs.items()])))
                self.logger.error(message)
                __shutdown(self, code)
        return wrapper
    return _try_inputs
