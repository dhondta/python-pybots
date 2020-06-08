# -*- coding: UTF-8 -*-
"""Functions for getting addresses of public proxies.

"""
import simplejson
import random
import re
try:  # Python3
    from urllib.parse import urlparse
except ImportError:  # Python2
    from urlparse import urlparse
try:
    from pycountry import countries
    pycountry_enabled = True
except ImportError:
    pycountry_enabled = False

from .common import filter_sources
from ..protocols.http import HTTPBot


__all__ = __features__ = [
    "find_public_http_proxy", "find_public_http_proxies_list", "get_public_http_proxies_sources",
    "find_public_socks_proxy", "find_public_socks_proxies_list", "get_public_socks_proxies_sources",
]


get_public_http_proxies_sources  = lambda: ["GatherProxy"]
get_public_socks_proxies_sources = lambda: ["MyProxySocks4", "MyProxySocks5"]


def __find_public_proxy(protocol="http", country=None, netloc=None, verbose=False):
    """ Private function for calling the right public proxy finding method. """
    l = eval("find_public_{}_proxies_list(country, netloc, verbose)".format(protocol.lower()))
    if len(l) > 0:
        return random.choice(l)


def __find_public_proxies_list(protocol="http", country=None, netloc=None,
                               verbose=False):
    """ Private function for calling the right public proxy listing method. """
    for proxy_lst_cls in filter_sources("PUB_{}_PROXY_SOURCES".format(protocol.upper()), netloc):
        p = eval(proxy_lst_cls)(verbose=verbose)
        if p.enabled:
            return p.get(country=country)


def find_public_http_proxy(country=None, netloc=None, verbose=False):
    """
    Selection function for getting the address of a public HTTP proxy.

    :param country: origin country of the public proxy
    :param netloc:  network location of the source for public proxy lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        public HTTP proxy address
    """
    return __find_public_proxy("http", country=country, netloc=netloc, verbose=verbose)


def find_public_socks_proxy(country=None, netloc=None, verbose=False):
    """
    Selection function for getting the address of a public Socks proxy.

    :param country: origin country of the public proxy
    :param netloc:  network location of the source for public proxy lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        public Socks proxy address
    """
    return __find_public_proxy("socks", country=country, netloc=netloc, verbose=verbose)


def find_public_http_proxies_list(country=None, netloc=None, verbose=False):
    """
    Selection function for getting a list of public HTTP proxies list.

    :param country: origin country of the public proxy
    :param netloc:  network location of the source for public proxy lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        list of public HTTP proxy addresses
    """
    return __find_public_proxies_list("http", country=country, netloc=netloc, verbose=verbose)


def find_public_socks_proxies_list(country=None, netloc=None, verbose=False):
    """
    Selection function for getting a list of public Socks proxies list.

    :param country: origin country of the public proxy
    :param netloc:  network location of the source for public proxy lookup
    :param verbose: enable lookup bot's versbose mode
    :return:        list of public HTTP proxy addresses
    """
    return __find_public_proxies_list("socks", country=country, netloc=netloc, verbose=verbose)


class PublicProxyList(object):
    def __init__(self, test=True, verbose=False):
        """
        Check if the given URL is valid at initialization.
        """
        url = urlparse(getattr(self, "url", ""))
        if url.netloc == "":
            raise ValueError("Public proxy URL not set correctly")
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
        # proxy entries are dynamically computed ; parse the scripts searching for entries to be converted to JSON
        _ = soup.find_all('script')
        p = "gp.insertPrx("
        _ = filter(lambda x: p in x.text, _)
        _ = map(lambda x: simplejson.loads(x.encode('utf-8').split(p, 1)[1].split(")", 1)[0]), _)
        _ = filter(lambda x: x['PROXY_TYPE'] == "Transparent", _)
        _ = filter(lambda x: x['PROXY_STATUS'] == "OK", _)
        # now collect proxy addresses and ports
        for p in _:
            proxies.append("http://%s:%s/" % (p['PROXY_IP'], int(p['PROXY_PORT'], 16)))
        return proxies


class MyProxySocks4(PublicProxyList):
    url = "https://www.my-proxy.com/free-socks-4-proxy.html"
    version = 4

    def get(self, country=None, *args, **kwargs):
        """
        Retrieve and parse the list of public proxies from GatherProxy.
        
        :param country: public proxy hosting country 2-uppercase format or country name if pycountry installed
        :return:        list of available public proxies
        """
        proxies = []
        # convert the country if necessary
        if country is not None:
            if pycountry_enabled:
                if not re.match(r'^[A-Z]{2}$', country):
                    converted = False
                    for arg in ["name", "official_name", "alpha_3"]:
                        try:
                            country = countries.get(**{arg: country}).alpha_2
                            converted = True
                            break
                        except KeyError:
                            pass
                    if not converted:
                        self.logger.error("Input country does not exist")
                        return []
            elif not re.match(r'^[A-Z]{2}$', country):
                self.logger.error("Bad country")
                return []
        # get the list from the Web page
        with HTTPBot(self.base, verbose=self.verbose) as bot:
            bot.get()
            soup = bot.soup
        # now collect proxy addresses and ports
        try:
            _ = soup.find_all('div', {'class': "list"})[0]
            for entry in _.text.split("<br>"):
                proxy, country_code = entry.split('#')
                if country is None or country_code == country:
                    proxies.append("socks{}://{}/".format(self.version, proxy))
        except:
            pass
        return proxies


class MyProxySocks5(MyProxySocks4):
    url = "https://www.my-proxy.com/free-socks-5-proxy.html"
    version = 5

