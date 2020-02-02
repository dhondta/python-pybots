"""Useful objects and functions for optional use in bots.

This package provides some useful objects and functions for use with bots.

"""
#TODO: remove these imports from the whole library
import base64
import os
import re
import urllib
from six import string_types

from .api import *
from .common import *
from .ip import *
from .proxy import *

#from .cryptography import *
#from .notations import *

from .api import __features__ as _api
from .common import __features__ as _common
from .ip import __features__ as _ip
from .proxy import __features__ as _proxy


__all__ = __features__ = ["base64", "os", "re", "string_types", "urllib"] + \
                         _api + _common + _ip + _proxy
