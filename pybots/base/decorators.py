#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Decorators for bot methods.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.1"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["try_or_die", "try_and_pass", "try_and_warn"]


import sys


def applicable_to(*bot_classes):
    """
    Class decorator for checking that a class is well inherited from any given
     parent bot class. Used in checking mixins' compatibility.

    :param bot_classes: list of compatible parent bot classes
    """
    def _applicable_to(cls):
        class NewClass(cls):
            def __init__(self, *args, **kwargs):
                parents = [c.__name__ for c in self.__class__.__mro__]
                assert any(bc in parents for bc in bot_classes), \
                    "This class is not compatible with any given parent" \
                    " classes ({})".format(", ".join(bot_classes))
                super(NewClass, self).__init__(*args, **kwargs)
        return NewClass
    return _applicable_to


def try_or_die(message, exc=Exception, extra_info=""):
    """
    Decorator handling a try-except block to log an error.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param extra_info: class attribute name whose value is to be displayed as
                        additional information
    """
    def _try_or_die(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                self.logger.critical(message)
                if hasattr(self, extra_info) and \
                    len(self.extra_info) > 0:
                    self.logger.info(getattr(self, extra_info))
                self.__exit__(*sys.exc_info())
        return wrapper
    return _try_or_die


def try_and_pass(exc=Exception):
    """
    Decorator handling a try-except block that simply continue the execution
     of the bot with no message in case of failure.

    :param exc: exception class on which the error is thrown
    """
    def _try_and_pass(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                pass
        return wrapper
    return _try_and_pass


def try_and_warn(message, exc=(AttributeError, IndexError), trace=False,
                 extra_info=""):
    """
    Decorator handling a try-except block to log a warning and continue
     the execution of the bot.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param trace:      display exception traceback
    :param extra_info: class attribute name whose value is to be displayed as
                        additional information
    """
    def _try_and_warn(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exc:
                self.logger.warn(message)
                if trace:
                    self.logger.exception(exc)
                if hasattr(self, extra_info):
                    self.logger.info(getattr(self, extra_info))
        return wrapper
    return _try_and_warn
