# -*- coding: UTF-8 -*-
"""Mixins for crawling Web pages.

This mixin allows to add a crawling functionality to a bot, available through a 'crawl(url)' method.

"""
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from tinyscript.helpers.decorators import *

from ..utils.common import urljoin, urlparse


__all__ = ["CrawlerMixin"]


@applicable_to("WebBot")
class CrawlerMixin(object):
    @try_and_warn("Crawling failed", trace=True)
    def crawl(self, url=None, *args, **kwargs):
        """
        Crawl the given URL.
        
        :param url:           URL to be crawled
        :param args:          arguments to be passed to self.get()
        :param random_uagent: randomize the User-Agent
        :param google_bot:    set the User-Agent of a Google bot
        :param kwargs:        keyword-arguments to be passed to self.get()
        """
        ragent = self._get_option('crawler', 'random_uagent', False, kwargs)
        gbot = self._get_option('crawler', 'google_bot', False, kwargs)
        url = url or self.url
        if urlparse(url).netloc == '':
            url = urljoin(self.url, url)
        if not hasattr(self, "crawled_urls"):
            self.crawled_urls = []
        h = kwargs.get('aheaders', {})
        if ragent:
            h['User-Agent'] = generate_user_agent()
        elif gbot:
            h['User-Agent'] = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        self.get(url, *args, **kwargs)
        if self.response.status_code == 200:
            self.crawled_urls.append(url)
            for link in BeautifulSoup(self.response.text).find_all('a'):
                self.crawl(link.get('href'), *args, **kwargs)

