"""Mixins for optional use in some bots.

This package provides some additional features to be used as mixins in bots.

"""
from .crawler import *
from .downloader import *
from .proxy import *

from .crawler import __features__ as _crawler
from .downloader import __features__ as _downloader
from .proxy import __features__ as _proxy


__all__ = __features__ = _crawler + _downloader + _proxy
