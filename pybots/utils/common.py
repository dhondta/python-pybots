#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Utility functions for other modules of this subpackage.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["bruteforce", "execute", "filter_sources"]


import string
from itertools import chain, product
from subprocess import Popen, PIPE


ALL_CHARS = list(map(chr, range(256)))


def bruteforce(max_len, alphabet=ALL_CHARS, from_zero=True):
    """
    Generator for bruteforcing according to a maximum length and an alphabet.
     2 behaviors are possible:
     - from_zero=True:  this will generate entries from length=1 to max_len
     - from_zero=False: this will generate entries of length=max_len only
    
    :yield: bruteforce entry
    """
    for i in range(*[1 if from_zero else max_len, max_len + 1]):
        for c in product(alphabet, repeat=i):
            yield c if isinstance(c[0], int) else ''.join(c)


def execute(cmd):
    """
    Simple wrapper for subprocess.Popen.
    
    :param cmd: command string
    """
    return Popen(cmd.split(), stdout=PIPE, stderr=PIPE).communicate()


def filter_sources(sources_list, netloc=None):
    """
    Selection function either for getting a shuffled list of selected sources or
     a single source filtered by its network location.

    :param sources: reference list of sources
    :param netloc:  network location of the source
    :return:        list of selected sources
    """
    if netloc is not None:
        sources = []
        for s in sources_list:
            if netloc == urlparse(s[1]).netloc:
                sources.append(s)
                break
    else:
        sources = [s for s in sources_list]
        random.shuffle(sources)
    return sources
