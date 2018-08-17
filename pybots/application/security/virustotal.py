#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client dedicated to VirusTotal API.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["VirusTotalBot"]


from pybots.specific.json import JSONBot


DOM = "https://virustotal.com"
REQ = "/vtapi/v2/"
RES = {
    'file': ["scan", "rescan", "report"],
    'url': ["scan", "report"],
    'domain': ["report"],
    'ip-address': ["report"],
    'comments': ["put"],
}


class VirusTotalBot(JSONBot):
    """
    VirusTotalBot class for communicating with the API v2 of VirusTotal.
    https://www.virustotal.com/es/documentation/public-api/

    :param api_key: API key
    :param verbose: debug level
    """
    def __init__(self, api_key, verbose=False):
        super(VirusTotalBot, self).__init__(DOM, verbose)
        self.api_key = api_key

    def __get(self, method, restype, action, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param restype: resource type (host, url, domain, ip, comments)
        """
        assert method in ["get", "post"]
        assert restype in RES.keys()
        assert action in RES[restype]
        url = REQ + "{}/{}".format(restype, action)
        params = kwargs.pop('params', {})
        params['apikey'] = self.api_key
        getattr(self, method)(url, params=params, **kwargs)

    def file_scan(self, filename):
        """
        Sending and scanning files.
        https://www.virustotal.com/es/documentation/public-api/#scanning-files

        :param filename: local filename
        """
        try:
            files = {'file': (filename, open(filename, 'rb'))}
        except IOError:
            self.logger.error("File does not exist !")
            return
        self.__get("post", "file", "scan", files=files)

    def file_rescan(self, resource):
        """
        Rescanning already submitted files.
        https://www.virustotal.com/es/documentation/public-api/#rescanning-files

        :param resource: resource's identifier (md5/sha1/sha256 hash, filename)
        """
        params = {'resource': resource}
        self.__get("post", "file", "rescan", params=params)

    def file_report(self, resource):
        """
        Retrieving file scan reports.
        https://www.virustotal.com/es/documentation/public-api/#getting-file-scans

        :param resource: resource's identifier (md5/sha1/sha256 hash, filename)
        """
        params = {'resource': resource}
        self.__get("post", "file", "report", params=params)

    def url_scan(self, url):
        """
        Sending and scanning URLs.
        https://www.virustotal.com/es/documentation/public-api/#scanning-urls

        :param url: URL that should be scanned
        """
        params = {'url': url}
        self.__get("post", "url", "report", params=params)

    def url_report(self, resource, scan=False):
        """
        Retrieving URL scan reports.
        https://www.virustotal.com/es/documentation/public-api/#getting-url-scans

        :param resource: scanned URL
        :param scan:     (optional) when set to "1" will automatically submit
                          the URL for analysis if no report is found
        """
        params = {'resource': url, 'scan': str(int(scan))}
        self.__get("post", "url", "report", params=params)
        if scan:
            try:
                return self.json['scan_id']
            except KeyError:
                return

    def ip_report(self, ip):
        """
        Retrieving IP address reports.
        https://www.virustotal.com/es/documentation/public-api/#getting-ip-reports

        :param ip: a valid IPv4 address in dotted quad notation
        """
        params = {'ip': ip}
        self.__get("get", "ip-address", "report", params=params)

    def domain_report(self, domain):
        """
        Retrieving domain reports.
        https://www.virustotal.com/es/documentation/public-api/#getting-domain-reports

        :param domain: domain name
        """
        params = {'domain': domain}
        self.__get("get", "domain", "report", params=params)

    def comment_put(self, resource, comment):
        """
        Make comments on files and URLs.
        https://www.virustotal.com/es/documentation/public-api/#making-comments

        :param resource: either a md5/sha1/sha256 hash of the file for review or
                          the URL to be commented on
        :param comment:  the actual review, you can tag it using the "#" twitter
                          -like syntax (e.g. #disinfection #zbot) and reference
                          users using the "@" syntax (e.g. @VirusTotalTeam).
        """
        params = {'resource': resource, 'comment': comment}
        self.__get("post", "comment", "put", params=params)
