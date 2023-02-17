"""CTF-related bots.

This package provides some bot implementations for managing the resolution of
 coding challenges in an automated way with some CTF websites.

"""
from .ringzero import *
from .rootme import *
from .zsis import *

from .ringzero import __all__ as _ringzero
from .rootme import __all__ as _rootme
from .zsis import __all__ as _zsis


__all__ = _ringzero + _rootme + _zsis

