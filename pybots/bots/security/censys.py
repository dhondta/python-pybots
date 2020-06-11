# -*- coding: UTF-8 -*-
"""Bot dedicated to Censys.

"""
from collections import OrderedDict

from ...apis import CensysAPI


__all__ = ["CensysBot"]


def reformat(response, hosts=None):
    hosts = hosts or {}
    for host in response.get('results', response):
        ip = host['ip']
        hosts[ip] = OrderedDict()
        hosts[ip]['Ports'] = ", ".join(host.get('protocols', []))
        hosts[ip]['Country'] = host.get('location.country', "")
    return hosts


class CensysBot(CensysAPI):
    """
    Class for requesting multiple information using the Censys API.

    :param api_id:     API identifier
    :param api_secret: API secret
    :param args:       JSONBot / API arguments
    :param kwargs:     JSONBot keyword-arguments
    """
    def hosts_from_file(self, ips_path):
        """
        Check a list of IP addresses from a given file.
        
        :param ips_path: path to the file with the list of IP addresses or networks (in CIDR notation)
        :return:         dictionary of hosts found on Censys
        """
        found = {}
        with open(ips_path) as f:
            for ip in f:
                found.update(reformat(self.search.ipv4("ip: %s" % ip.strip(),
                                                       fields=["ip", "protocols", "location.country"]), found))
        return found
    
    def hosts_from_list(self, *ips):
        """
        Check a list of IP addresses from the given arguments.
        
        :param ips: list of IP addresses or networks (in CIDR notation)
        :return:    dictionary of hosts found on Censys
        """
        found = {}
        for ip in ips:
            found.update(reformat(self.search.ipv4("ip: %s" % ip.strip(),
                                                   fields=["ip", "protocols", "location.country"]), found))
        return found

