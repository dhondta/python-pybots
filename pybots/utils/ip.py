#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Simple function for getting own public IP.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["find_public_http_proxy", "find_public_http_proxies_list",
           "get_my_ip", "get_my_ip_sources", "get_public_http_proxies_sources"]


import json
import random
try:  # Python3
    from urllib.parse import urlparse
except ImportError:  # Python2
    from urlparse import urlparse

from pybots.specific import HTTPBot, JSONBot


MY_IP_SOURCES = [
    (HTTPBot, "http://ip.42.pl/raw", lambda x: x.response.text),
    (HTTPBot, "https://api.ip.sb/ip", lambda x: x.response.text),
    (JSONBot, "http://jsonip.com", lambda x: x.json['ip']),
    (JSONBot, "https://ip.seeip.org/jsonip", lambda x: x.json['ip']),
    (JSONBot, "http://httpbin.org/ip", lambda x: x.json['origin']),
    (JSONBot, "http://ip-api.com/json", lambda x: x.json['query']),
    (JSONBot, "https://api.ipify.org/?format=json", lambda x: x.json['ip']),
    (JSONBot, "https://wtfismyip.com/json",
     lambda x: x.json['YourFuckingIPAddress']),
]
PUB_PROXY_SOURCES = [
    "GatherProxy",
]


get_my_ip_sources = lambda: [urlparse(s[1]).netloc for s in MY_IP_SOURCES]
get_public_http_proxies_sources = lambda: PUB_PROXY_SOURCES


def _filter_sources(sources_list, source=None):
    """
    Selection function for getting a list of selected sources.

    :param sources: reference list of sources
    :param source:  network location of the source
    :return:        list of selected sources
    """
    if source is not None:
        sources = []
        for s in sources_list:
            if source == urlparse(s[1]).netloc:
                sources.append(s)
                break
    else:
        sources = [s for s in sources_list]
        random.shuffle(sources)
    return sources


def find_public_http_proxy(country=None, source=None, verbose=False):
    """
    Selection function for getting the address of a public HTTP proxy.

    :param country: origin country of the public proxy
    :param source:  network location of the source for public IP lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        public HTTP proxy address
    """
    l = find_public_http_proxies_list(country, source, verbose)
    if len(l) > 0:
        return random.choice(l)


def find_public_http_proxies_list(country=None, source=None, verbose=False):
    """
    Selection function for getting a list of public HTTP proxies list.

    :param country: origin country of the public proxy
    :param source:  network location of the source for public IP lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        list of public HTTP proxy addresses
    """
    for proxy_lst_cls in _filter_sources(PUB_PROXY_SOURCES, source):
        p = eval(proxy_lst_cls)(verbose=verbose)
        if p.enabled:
            return p.get(country=country)


def get_my_ip(source=None, only_https=False, verbose=False):
    """
    Simple function for getting own public IP.

    :param source:     network location of the source for public IP lookup
    :param only_https: only request own public IP through HTTPS
    :param verbose:    enable lookup bot's versbose mode
    :return:           own public IP
    """
    for bot_cls, url, transform in _filter_sources(MY_IP_SOURCES, source):
        url = urlparse(url)
        if only_https and url.scheme == "https":
            continue
        with bot_cls("{}://{}".format(url.scheme, url.netloc), verbose=verbose,
                     random_uagent=True) as bot:
            bot.logger.debug("Trying to get public IP with '{}'..."
                             .format(url.netloc))
            if url.query != '':
                bot.get("{}?{}".format(url.path, url.query))
            else:
                bot.get(url.path)
            if bot.response.status_code == 200:
                try:
                    return transform(bot).strip()
                except:
                    bot.logger.debug("Bad response")
            elif verbose:
                bot.logger.debug("Request for own public IP failed")


class PublicProxyList(object):
    def __init__(self, test=True, verbose=False):
        """
        Check if the given URL is valid at initialization.
        """
        url = urlparse(getattr(self, "url", ""))
        assert url.netloc != '', "Public proxy URL not set correctly"
        self.name = url.netloc.split('.')[-2].lower()
        self.base = "{}://{}".format(url.scheme, url.netloc)
        self.path = url.path
        self.verbose = verbose
        if test:
            with HTTPBot(self.base, verbose=verbose) as bot:
                bot.get()
                self.enabled = bot.response.status_code == 200

    def get(self, *args, **kwargs):
        """
        Default method, returning empty list of proxies.
        """
        return []


class GatherProxy(PublicProxyList):
    url = "http://www.gatherproxy.com/proxylist/country/"

    def get(self, country=None, *args, **kwargs):
        """
        Retrieve and parse the list of public proxies from GatherProxy.
        
        :param country: public proxy hosting country name
        :return:        list of available public proxies
        """
        proxies = []
        # get the list from the Web page
        with HTTPBot(self.base, verbose=self.verbose) as bot:
            if country is None:
                bot.get()
            else:
                bot.get(self.path, params={'c': country})
            soup = bot.soup
        # proxy entries are dynamically computed ; parse the scripts searching
        #  for entries to be converted to JSON and filtered
        _ = soup.find_all('script')
        p = "gp.insertPrx("
        _ = filter(lambda x: p in x.text, _)
        _ = map(lambda x: json.loads(x.encode('utf-8').split(p, 1)[1]\
                                                      .split(")", 1)[0]), _)
        _ = filter(lambda x: x['PROXY_TYPE'] == "Transparent", _)
        _ = filter(lambda x: x['PROXY_STATUS'] == "OK", _)
        # now collect proxy addresses and ports
        for p in _:
            proxies.append("http://%s:%s/" % (p['PROXY_IP'],
                                              int(p['PROXY_PORT'], 16)))
        return proxies
