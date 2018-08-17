#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Mixins for crawling Web pages.

This mixin allows to add a crawling functionality to a bot, available through a
 'crawl(url)' method.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["CrawlerMixin"]


import requests
from bs4 import BeautifulSoup
try:  # Python3
    from urllib.parse import urljoin, urlparse
except ImportError:  # Python2
    from urlparse import urljoin, urlparse

from pybots.base.decorators import *


@applicable_to("WebBot")
class CrawlerMixin(object):
    @try_and_warn("Crawling failed", trace=True)
    def crawl(self, url=None, behave_like_google_bot=False):
        url = url or self.url
        if urlparse(url).netloc == '':
            url = urljoin(self.url, url)
        if not hasattr(self, "crawled_urls"):
            self.crawled_urls = []
        headers = {"User-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; "
                                 "+http://www.google.com/bot.html)"} \
                  if behave_like_google_bot else {}
        self.get(url, aheaders=headers)
        if self.response.status_code == 200:
            self.crawled_urls.append(url)
            for link in BeautifulSoup(self.response.text).find_all('a'):
                self.crawl(link.get('href'), behave_like_google_bot)
