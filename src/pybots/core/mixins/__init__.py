"""Mixins for optional use in some bots.

This package provides some additional features to be used as mixins in bots.

"""
from .crawler import *
from .downloader import *
from .mailer import *
from .proxy import *

from .crawler import __all__ as _crawler
from .downloader import __all__ as _downloader
from .mailer import __all__ as _mailer
from .proxy import __all__ as _proxy


__all__ = __features__ = _crawler + _downloader + _mailer + _proxy

