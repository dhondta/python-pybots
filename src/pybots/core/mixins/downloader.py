# -*- coding: UTF-8 -*-
"""Mixins for bulk-downloading resources based on a list of URL's.

This mixin allows to add a list-based bulk-download functionality to a WebBot, available through a 'bulk_download()' method.

"""
from os import makedirs
from os.path import basename, dirname, exists, isdir, isfile, join, splitext
from tinyscript.helpers.decorators import *


__all__ = ["BulkDownloadMixin"]


@applicable_to("WebBot")
class BulkDownloadMixin(object):
    @try_and_warn("Bulk download failed", trace=True)
    def bulk_download(self, *urls, **kwargs):
        """
        Bulk-download URL's, mixed from a list or from a file.

        :param urls:      list of URL's or request paths
        :param from_file: file with a list of URL's or request paths
        :param dest:      destination folder
        """
        dest = self._get_option('downloader', 'destination_path', ".", kwargs)
        from_file = self._get_option('downloader', 'from_file', None, kwargs)
        urls = list(urls)
        if isfile(from_file):
            with open(from_file) as f:
                for l in f:
                    l = l.strip()
                    if not l.startswith('#') and not l in urls:
                        urls.append(l)
        if len(urls) == 0:
            return
        if not exists(dest):
            makedirs(dest)
        elif not isdir(dest):
            self.logger.error("{} is not a directory !".format(dest))
            return
        undef_res_counter = 2
        for url in urls:
            parsed = urlparse(url)
            filename = basename(parsed.path) or "undefined"
            dirpath = join(dest, dirname(parsed.path))
            filepath = join(dirpath, filename)
            if not exists(dirpath):
                makedirs(dirpath)
            elif exists(filepath):
                filename, ext = splitext(filename)
                filename = "{}-{}{}".format(filename, undef_res_counter, ext)
                filepath = join(dirpath, filename)
                undef_res_counter += 1
            self.retrieve(url, filepath)

