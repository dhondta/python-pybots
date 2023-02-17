"""Useful objects and functions for optional use in bots.

This package provides some useful objects and functions for use with bots.

"""
from .api import __features__ as _api
from .cloudflare import __features__ as _cloudflare
from .common import __features__ as _common
from .ip import __features__ as _ip
from .proxy import __features__ as _proxy


__all__ = __features__ = ["base64", "os", "re", "string_types", "urllib"] + _api + _cloudflare + _common + _ip + _proxy

