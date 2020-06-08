"""Core subpackage.

This subpackage contains:
- Base classes to be inherited while defining new bots
- Base classes implementing protocols, to be specialized in specific bots
- Mixin classes that can be appended to Bot classes for additional features
- Utility functions

"""
from .mixins import *
from .protocols import *

from .mixins import __features__ as _mixins
from .protocols import __features__ as _protocols


__all__ = _mixins + _protocols

