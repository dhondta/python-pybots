#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Utility functions for other modules of this subpackage.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["filter_sources"]


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
