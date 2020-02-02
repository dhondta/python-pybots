"""Core subpackage.

This subpackage contains:
- Base classes to be inherited while defining new bots
- Base classes implementing protocols, to be specialized in specific bots
- Mixin classes that can be appended to Bot classes for additional features
- Utility functions

"""

from .mixins import *
from .protocols import *
