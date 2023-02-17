# -*- coding: UTF-8 -*-
"""Bot dedicated to Censys.

"""
from collections import OrderedDict

from ...apis import CensysAPI
from ...core.utils.api import NoResultError


__all__ = ["CensysBot"]


def _dn2dict(s):
    """
    This utility function converts a string of type "O=val1, CN=val2, ..." into a dictionary
     {'Organization': "val1", 'CName': "val2", ...}.
    """
    d = {}
    for p in s.split(", "):
        try:
            k, v = p.split("=")
            k = "Organization" if k == "O" else "CName" if k == "CN" else "Country" if k == "C" else k
            d[k] = v
        except ValueError:
            d[k] += ", " + p
    return d


def _getall(m):
    """
    This decorator aims to make the given method consider all the available pages related to its request. This avoids
     rewriting loops for downloading them all when multiple pages of results are available.
    """
    def _wrapper(self, *args, **kwargs):
        r = m(self, *args, **kwargs)
        curr_page = args[1] if len(args) > 1 else kwargs.get('page', 1)
        if r['status'] != "ok" or r.get('metadata') is None or r['metadata']['count'] == 0:
            raise NoResultError()
        if r['metadata']['pages'] > 1:
            pages = list(range(1, r['metadata']['pages'] + 1))
            pages.remove(curr_page)
            for page in pages:
                # CONVENTION: when relevant, 'page' appears as the SECOND argument in 'args'
                #  therefore, if 'args' has at least 2 elements, use it for completing the 'page' parameter ;
                #  otherwise, use 'kwargs'
                if len(args) > 1:
                    args = args[:1] + (page,) + args[2:]
                    kwargs.pop('page', None)
                else:
                    kwargs['page'] = page
                r2 = m(self, *args, **kwargs)
                for k in r['metadata'].keys():
                    v1, v2 = r['metadata'][k], r2['metadata'][k]
                    if v1 != v2 and isinstance(v1, int):
                        r['metadata'][k] += r2['metadata'][k]
                r['results'].extend(r2['results'])
            r['results'].sort(key=lambda x: x[list(x.keys())[0]])
            del r['metadata']['page']
        return r
    return _wrapper


class CensysBot(CensysAPI):
    """
    Class for requesting multiple information using the Censys API.

    :param api_id:     API identifier
    :param api_secret: API secret
    :param args:       JSONBot / API arguments
    :param kwargs:     JSONBot keyword-arguments
    """
    def hosts_from_certificate(self, *domains, **kwargs):
        """
        Enumerate hostnames for the input domains from the Certificate Transparency Logs.
        
        :param domains: list of domains
        :return:        dictionary of domain names found with their fingerprints
        """
        found, expired, _ = {}, kwargs.pop('expired', True), kwargs.pop('no_regex', None)
        kwargs['fields'] = kwargs.pop('fields', ["parsed"]) + ["tags"]
        for domain in domains:
            for cert in _getall(self.search.certificates)(domain, no_regex=True, **kwargs)['results']:
                dom = _dn2dict(cert['parsed.subject_dn'])['CName']
                if dom.endswith(domain):
                    found.setdefault(dom, [])
                    d = {'Fingerprint': cert['parsed.fingerprint_sha256'], 'Issuer': _dn2dict(cert['parsed.issuer_dn']),
                         'Names': cert['parsed.names']}
                    if not expired:
                        if "expired" in cert['tags']:
                            continue
                    else:
                        d['Expired'] = "expired" in cert['tags']
                    found[dom].append(d)
        return found
    hosts_from_certificates = hosts_from_certificate
    
    def hosts_from_domains_file(self, domains_path, **kwargs):
        """
        Check a list of domain names from a given file.
        
        :param domains_path: path to the file with the list of domain names
        :return:             dictionary of hosts found on Censys
        """
        found = []
        with open(domains_path) as f:
            for d in f:
                found.extend(self.hosts_from_certificate(d.strip(), **kwargs))
        return list(set(found))
    
    def hosts_from_ip(self, *ips):
        """
        Check a list of IP addresses from the given arguments.
        
        :param ips: list of IP addresses or networks (in CIDR notation)
        :return:    dictionary of hosts found on Censys
        """
        found = {}
        for ip in ips:
            r = _getall(self.search.ipv4)("ip: %s" % ip.strip(), fields=["ip", "protocols", "location.country"])
            for h in r.get('results', r):
                ip = h['ip']
                found[ip] = {}
                found[ip]['Ports'] = ", ".join(h.get('protocols', []))
                found[ip]['Country'] = h.get('location.country', "")
        return found
    hosts_from_ips = hosts_from_ip
    
    def hosts_from_ips_file(self, ips_path):
        """
        Check a list of IP addresses from a given file.
        
        :param ips_path: path to the file with the list of IP addresses or networks (in CIDR notation)
        :return:         dictionary of hosts found on Censys
        """
        found = {}
        with open(ips_path) as f:
            for ip in f:
                found.update(self.hosts_from_ip(ip.strip()))
        return found

