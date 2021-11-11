"""Web API's for default credentials found on the Internet.

This package provides some API's for various websites proposing lists of default credentials.

"""

from .cirtnet import *
from .datarecovery import *
from .passworddb import *
from .routerpasswd import *
from .saynamweb import *

from .cirtnet import __all__ as _cirtnet
from .datarecovery import __all__ as _dr
from .passworddb import __all__ as _pswddb
from .routerpasswd import __all__ as _rtrpaswd
from .saynamweb import __all__ as _saynamweb


__all__ = _cirtnet + _dr + _pswddb + _rtrpaswd + _saynamweb

