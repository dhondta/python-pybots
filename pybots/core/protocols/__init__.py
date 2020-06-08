"""Specific-purpose bots.

This package provides specific-purpose bot implementations for managing sessions
 with remote hosts in an automated way according to specific protocols.

"""
from .http import *
from .irc import *
from .tcp import *

from .http import __features__ as _http
from .irc import __features__ as _irc
from .tcp import __features__ as _tcp


__all__ = __features__ = _http + _irc + _tcp

