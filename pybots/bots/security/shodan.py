# -*- coding: UTF-8 -*-
"""Bot dedicated to Shodan.

"""
from collections import OrderedDict

from ...apis import ShodanAPI


__all__ = ["ShodanBot"]


def reformat(response, hosts=None):
    hosts = hosts or {}
    for host in response.get('matches', [response]):
        ip = host['ip_str']
        service = OrderedDict()
        service['Port'] = "{}/{}".format(host['transport'], host['port'])
        service['Name'] = "{} {}".format(host.get('product', ""), host.get('version', "")).strip()
        service['CPE'] = ", ".join(host.get('cpe', []))
        if ip in hosts.keys():
            hosts[ip]['Services'].append(service)
        else:
            hosts[ip] = OrderedDict()
            hosts[ip]['Location'] = "{} ({})".format(host['location'].get('city') or "?",
                                                     host['location'].get('country_code'))
            hosts[ip]['Organization'] = host['org']
            hosts[ip]['ISP'] = host['isp']
            hosts[ip]['Last Update'] = host['timestamp']
            hosts[ip]['Hostnames'] = ", ".join(host['hostnames'])
            hosts[ip]['ASN'] = host['asn']
            hosts[ip]['Services'] = [service]
    for data in hosts.values():
        data['Services'] = sorted(data['Services'], key=lambda x: int(x['Port'].split("/")[-1]))
    return hosts


class ShodanBot(ShodanAPI):
    """
    Class for requesting multiple information using the Shodan API.

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    def hosts_from_file(self, ips_path):
        """
        Check a list of IP addresses from a given file.
        
        :param ips_path: path to the file with the list of IP addresses or networks (in CIDR notation)
        :return:         dictionary of hosts found on Shodan
        """
        found = {}
        with open(ips_path) as f:
            for ip in f:
                found.update(reformat(self.shodan.host.search("net:%s" % ip.strip()), found))
        return found
    
    def hosts_from_list(self, *ips):
        """
        Check a list of IP addresses from the given arguments.
        
        :param ips: list of IP addresses or networks (in CIDR notation)
        :return:    dictionary of hosts found on Shodan
        """
        found = {}
        for ip in ips:
            found.update(reformat(self.shodan.host.search("net:%s" % ip.strip()), found))
        return found

