# -*- coding: UTF-8 -*-
"""Simple function for getting own public IP.

"""
try:  # Python3
    from urllib.parse import urlparse
except ImportError:  # Python2
    from urlparse import urlparse

from .common import filter_sources
from ..protocols.http import HTTPBot, JSONBot


__all__ = __features__ = ["get_my_public_ip", "get_my_public_ip_sources"]

MYIP_SOURCES = [
    (HTTPBot, "http://ip.42.pl/raw", lambda x: x.response.text),
    (HTTPBot, "https://api.ip.sb/ip", lambda x: x.response.text),
    (JSONBot, "http://jsonip.com", lambda x: x.json['ip']),
    (JSONBot, "https://ip.seeip.org/jsonip", lambda x: x.json['ip']),
    (JSONBot, "http://httpbin.org/ip", lambda x: x.json['origin']),
    (JSONBot, "http://ip-api.com/json", lambda x: x.json['query']),
    (JSONBot, "https://api.ipify.org/?format=json", lambda x: x.json['ip']),
    (JSONBot, "https://wtfismyip.com/json", lambda x: x.json['YourFuckingIPAddress']),
]
get_my_public_ip_sources = lambda: [urlparse(s[1]).netloc for s in MYIP_SOURCES]


def get_my_public_ip(source=None, only_https=False, verbose=False):
    """
    Simple function for getting own public IP.

    :param source:     network location of the source for public IP lookup
    :param only_https: only request own public IP through HTTPS
    :param verbose:    enable lookup bot's versbose mode
    :return:           own public IP
    """
    # FIXME: this does not use proxy !!!
    for bot_cls, url, transform in filter_sources(MYIP_SOURCES, source):
        url = urlparse(url)
        if only_https and url.scheme == "https":
            continue
        with bot_cls("{}://{}".format(url.scheme, url.netloc), verbose=verbose, random_uagent=True) as bot:
            bot.logger.debug("Trying to get public IP with '{}'...".format(url.netloc))
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

