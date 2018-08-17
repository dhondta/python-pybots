#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client dedicated to Shodan API.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["ShodanBot"]


from pybots.specific.json import JSONBot


DOM = "https://api.shodan.io"


class ShodanBot(JSONBot):
    """
    ShodanBot class for communicating with the API of Shodan.
    https://developer.shodan.io/api

    Note: All API methods are rate-limited to 1 request/ second.

    :param apikey:  API key
    :param verbose: debug level
    """
    def __init__(self, apikey, verbose=False):
        super(ShodanBot, self).__init__(DOM, verbose)
        self.apikey = apikey

    def __get(self, method, reqpath, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param reqpath: request path
        """
        getattr(self, method)(reqpath + "?key={}".format(self.apikey), **kwargs)

    def shodan_host(self, ip, history=False, minify=False):
        """
        Returns all services that have been found on the given host IP.
        
        :param ip:      host IP address
        :param history: True if all historical banners should be returned
        :param minify:  True to only return the list of ports and the general
                         host information, no banners
        """
        params = {'history': history, 'minify': minify}
        self.__get("get", "/shodan/host/{}".format(ip), params=params)

    def shodan_host_count(self, query, facets=None):
        """
        Returns the total number of results that matched the query and any facet
         information that was requested. As a result this method does not
         consume query credits.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary
                        information on
        """
        params = {'query': query}
        if facets is not None:
            params['facets'] = facets
        self.__get("get", "/shodan/host/count", params=params)

    def shodan_host_search(self, query, facets=None, page=1, minify=False):
        """
        Search Shodan using the same query syntax as the website and use facets
         to get summary information for different properties. This method may
         use API query credits depending on usage.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary
                        information on
        :param page:   page number to page through results 100 at a time
        :param minify: whether or not to truncate some of the larger fields
        """
        params = {'query': query, 'page': page, 'minify': minify}
        if facets is not None:
            params['facets'] = facets
        self.__get("get", "/shodan/host/count", params=params)

    def shodan_host_search_tokens(self, query):
        """
        Lets the user determine which filters are being used by the query string
         and what parameters were provided to the filters.

        :param query:  Shodan search query
        """
        params = {'query': query}
        self.__get("get", "/shodan/host/search/tokens", params=params)

    def shodan_ports(self):
        """
        Returns a list of port numbers that the crawlers are looking for.
        """
        self.__get("get", "/shodan/ports")

    def shodan_protocols(self):
        """
        Returns an object containing all the protocols that can be used when
         launching an Internet scan.
        """
        self.__get("get", "/shodan/protocols")

    def shodan_scan(self, ips):
        """
        Returns an object containing all the protocols that can be used when
         launching an Internet scan.

        Note: 1 IP consumes 1 scan credit

        :param ips: comma-separated list of IPs or netblocks (in CIDR notation)
                     that should get crawled
        """
        params = {'ips': ips}
        self.__get("post", "/shodan/protocols", params=params)

    def shodan_scan_internet(self, port, protocol):
        """
        Request Shodan to crawl the Internet for a specific port.

        Note: restricted to security researchers and companies with a Shodan
               Data license.

        :param port:     port that Shodan should crawl the Internet for
        :param protocol: name of the protocol that should be used to interrogate
                          the port (see shodan_protocols() for a list of
                          supported protocols)
        """
        params = {'ips': ips}
        self.__get("post", "/shodan/protocols", params=params)
