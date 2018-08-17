#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Mixins for bulk-downloading resources based on a list of URL's.

This mixin allows to add a list-based bulk-download functionality to a WebBot,
 available through a 'bulk_download()' method.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["BulkDownloadMixin"]


import os
from os.path import basename, dirname, exists, isdir, join, splitext

from pybots.base.decorators import *


@applicable_to("WebBot")
class BulkDownloadMixin(object):
    @try_and_warn("Bulk download failed", trace=True)
    def bulk_download(self, from_list=None, from_file=None, dest="."):
        """
        Method for bulk-downloading a list of resources.

        :parame from_list: list of URL's or request paths
        :parame from_file: file with a list of URL's or request paths
        :parame dest:      destination folder
        """
        assert from_list is not None or from_file is not None, \
            "At least one of from_list/from_file must be defined !"
        from_list = from_list or []
        if from_file is not None:
            with open(from_file) as f:
                for l in f:
                    l = l.strip()
                    if not l.startswith('#') and not l in from_list:
                        from_list.append(l)
        if len(from_list) == 0:
            return
        if not exists(dest):
            os.makedirs(dest)
        elif not isdir(dest):
            self.logger.error("{} is not a directory !".format(dest))
            return
        undef_res_counter = 2
        for resource in from_list:
            parsed = urlparse(resource)
            filename = basename(parsed.path) or "undefined"
            dirpath = join(dest, dirname(parsed.path))
            filepath = join(dirpath, filename)
            if not exists(dirpath):
                os.makedirs(dirpath)
            elif exists(filepath):
                filename, ext = splitext(filename)
                filename = "{}-{}{}".format(filename, undef_res_counter, ext)
                filepath = join(dirpath, filename)
                undef_res_counter += 1
            self.retrieve(resource, filepath)
