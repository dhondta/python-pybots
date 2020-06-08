# -*- coding: UTF-8 -*-
"""Common functions for other modules of this subpackage.

"""
try:  # PYTHON2
    from urlparse import urljoin, urlparse
except ImportError:
    from urllib.parse import urljoin, urlparse


__all__ = __features__ = ["filter_sources", "urljoin", "urlparse"]


def filter_sources(*sources, **kwargs):
    """
    Selection function either for getting a shuffled list of selected sources or
     a single source filtered by its network location.

    :param sources: reference list of sources
    :param netloc:  network location of the source
    :return:        list of selected sources
    """
    netloc = kwargs.get('netloc')
    if netloc is not None:
        l = []
        for s in sources:
            if netloc == urlparse(s[1]).netloc:
                l.append(s)
                break
    else:
        l = [s for s in sources]
        random.shuffle(l)
    return l

