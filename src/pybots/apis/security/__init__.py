"""Security-related Web service API's.

This package provides some implementations using various security-related Web service API's.

"""

from .data_breaches import *
from .default_credentials import *
from .exposed_devices import *
from .virustotal import *

from .data_breaches import __all__ as _db
from .default_credentials import __all__ as _dc
from .exposed_devices import __all__ as _ed
from .virustotal import __all__ as _vt


__all__ = _db + _dc + _ed + _vt

