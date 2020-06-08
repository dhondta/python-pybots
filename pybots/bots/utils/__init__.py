"""Miscellaneous bots.

This package provides some bot implementations for interacting with some
 well-known applications.

"""
from .git import *
from .postbin import *

from .git import __all__ as _git
from .postbin import __all__ as _postbin


__all__ = _git + _postbin

