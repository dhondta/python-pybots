#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Collection of commonly used regular expressions.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = [
    "RE_MD5", "is_md5",
    "RE_SHA1", "is_sha1",
    "RE_SHA224", "is_sha224",
    "RE_SHA256", "is_sha256",
    "RE_SHA384", "is_sha384",
    "RE_SHA512", "is_sha512",
    "RE_DOMAIN", "is_domain",
    "RE_EMAIL", "is_email",
    "RE_HOSTNAME", "is_hostname",
    "RE_IPV4", "is_ipv4",
]


import re


RE_MD5    = re.compile(r'\b[0-9a-f]{32}\b', re.I)
RE_SHA1   = re.compile(r'\b[0-9a-f]{40}\b', re.I)
RE_SHA224 = re.compile(r'\b[0-9a-f]{56}\b', re.I)
RE_SHA256 = re.compile(r'\b[0-9a-f]{64}\b', re.I)
RE_SHA384 = re.compile(r'\b[0-9a-f]{96}\b', re.I)
RE_SHA512 = re.compile(r'\b[0-9a-f]{128}\b', re.I)

# see: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s15.html
RE_DOMAIN   = re.compile(r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)'
                         r'*\.)+[a-z]{2,63}\b', re.I)
# see: https://stackoverflow.com/questions/201323/how-to-validate-an-email-address-using-a-regular-expression
RE_EMAIL    = re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*'
                         r'+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21'
                         r'\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*'
                         r'")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]'
                         r'(?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9]'
                         r')|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4]['
                         r'0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?'
                         r':[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\['
                         r'\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')
RE_HOSTNAME = re.compile(r'^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
                         r'([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$')
RE_IPV4     = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
                         r'\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]'
                         r')\b')
                     
is_md5    = lambda h: RE_MD5.match(h) is not None
is_sha1   = lambda h: RE_SHA1.match(h) is not None
is_sha224 = lambda h: RE_SHA224.match(h) is not None
is_sha256 = lambda h: RE_SHA256.match(h) is not None
is_sha384 = lambda h: RE_SHA384.match(h) is not None
is_sha512 = lambda h: RE_SHA512.match(h) is not None

is_domain   = lambda d: RE_DOMAIN.match(d) is not None
is_email    = lambda e: RE_EMAIL.match(e) is not None
is_hostname = lambda h: RE_HOSTNAME.match(h) is not None
is_ipv4     = lambda i: RE_IPV4.match(i) is not None
