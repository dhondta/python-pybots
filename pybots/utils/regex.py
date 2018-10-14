#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Collection of commonly used regular expressions.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["RE_MD5", "RE_SHA1", "RE_SHA224", "RE_SHA256", "RE_SHA384",
           "RE_SHA512", "RE_IPV4"]


import re


RE_MD5    = re.compile(r'\b[0-9a-f]{32}\b')
RE_SHA1   = re.compile(r'\b[0-9a-f]{40}\b')
RE_SHA224 = re.compile(r'\b[0-9a-f]{56}\b')
RE_SHA256 = re.compile(r'\b[0-9a-f]{64}\b')
RE_SHA384 = re.compile(r'\b[0-9a-f]{96}\b')
RE_SHA512 = re.compile(r'\b[0-9a-f]{128}\b')

RE_IPV4 = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.)'
                     r'{3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b')
