# -*- coding: UTF-8 -*-
"""API client dedicated to VirusTotal API.

"""
from tinyscript.helpers.data.types import *

from ...core.utils.api import *


__all__ = ["VirusTotalAPI"]


def valid_hash(f):
    if not (is_md5(f) or is_sha1(f) or is_sha256(f)):
        raise ValueError("not a valid resource hash")


class VirusTotalAPI(API):
    """
    Class for communicating with the API v2 of VirusTotal.
    
    Reference: https://developers.virustotal.com/reference

    :param api_key: API key
    :param public:  whether the usage of the API is public
    :param args:    JSONBot arguments
    :param kwargs:  JSONBot keyword-arguments
    """
    resource_types = {
        'file': ["behaviour", "download", "scan", "rescan", "report"],
        'url': ["scan", "report"],
        'domain': ["report"],
        'ip-address': ["report"],
        'comments': ["put"],
    }
    url = "https://www.virustotal.com"
    
    def __init__(self, api_key, public=True, *args, **kwargs):
        self.__api_info = None
        super(VirusTotalAPI, self).__init__(DOM, *args, **kwargs)
        self.api_key = api_key
        self.public = public
        self._disable_time_throttling = not public
    
    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if k == "action":
                if v not in self.resource_types[kwargs.get('restype')]:
                    raise ValueError("bad action (given the resource type)")
            elif k == "restype":
                if v not in self.resource_types.keys():
                    raise ValueError("bad resource type")

    @time_throttle(60, requests=4)
    def _request(self, method, restype, action, extra=None, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param restype: resource type (host, url, domain, ip, comments)
        :param action:  action item to be processed for the given resource
        :param extra:   additional URL subpath to be used
        """
        self.__validate(action=action, restype=restype)
        url = "/vtapi/v2/%s/%s" % (restype, action)
        if extra:
            url += "/%s" % extra
        url = kwargs.pop('override_url', None) or url
        params = kwargs.pop('params', {})
        params['apikey'] = self._api_key
        kwargs['params'] = params
        super(VirusTotalAPI, self)._request(url, method, **kwargs)

    # ------------------------------- COMMENTS ---------------------------------
    def comment_get(self, resource, before=None):
        """
        Get comments for a file or URL.
        
        :param resource: either a md5/sha1/sha256 hash of the file for review or
                          the URL to be commented on
        :param before:   datetime token for iterating over comments when the
                          resource has been commented on more than 25 times
        """
        valid_hash(resource)
        params = {'resource': resource}
        if before:
            params['before'] = before
        self.__get("get", "comment", "get", params=params)

    # -------------------------------- DOMAINS ---------------------------------
    def domain_report(self, domain):
        """
        Retrieves a domain report.
        
        :param domain: domain name
        """
        domain_name(domain)
        params = {'domain': domain}
        self.__get("get", "domain", "report", params=params)
    
    # --------------------------------- FILES ----------------------------------
    @private
    def file_behaviour(self, hash):
        """
        Retrieve behaviour report.
        
        :param hash: resource's hash (md5/sha1/sha256)
        """
        valid_hash(hash)
        params = {'hash': hash}
        self.__get("get", "file", "behaviour", params=params)
    
    @private
    def file_download(self, hash):
        """
        Download a file.
        
        :param hash: file's hash (md5/sha1/sha256)
        """
        valid_hash(hash)
        params = {'hash': hash}
        self.__get("get", "file", "download", params=params)
    
    @private
    def file_network_traffic(self, hash):
        """
        Retrieve network traffic report.
        
        :param hash: file's hash (md5/sha1/sha256) whose network traffic dump
        """
        valid_hash(hash)
        params = {'hash': hash}
        self.__get("get", "file", "download", params=params)

    def file_report(self, resource, allinfo=False):
        """
        Retrieve file scan reports.
        
        :param resource: resource's identifier (md5/sha1/sha256 hash, filename)
        :param allinfo:  return additional information about the file
        """
        params = {'resource': resource, 'allinfo': allinfo}
        self.__get("post", "file", "report", params=params)

    def file_rescan(self, resource):
        """
        Rescanning already submitted files.
        
        :param resource: resource's identifier (md5/sha1/sha256 hash, filename)
        """
        params = {'resource': resource}
        self.__get("post", "file", "rescan", params=params,
            aheaders={'Content-Type': "application/x-www-form-urlencoded"})

    def file_scan(self, filename):
        """
        Upload and scan a file.
        
        :param filename: local file to be scanned
        """
        files = {'file': (filename, open(filename, 'rb'))}
        s = os.stat(filename).st_size
        if s > 200*1024*1024:
            raise APIError("File is too big")
        kwargs = {'files': files}
        if s > 32*1024*1024:
            if self.public:
                raise APIError("File is too big")
            self.file_scan_upload_url()
            kwargs['override_url'] = self.json['upload_url']
        self.__get("post", "file", "scan", **kwargs)
    
    @private
    def file_scan_upload_url(self):
        """
        Get a URL for uploading files larger than 32MB.
        """
        self.__get("get", "file", "scan", "upload_url")
        self.json['upload_url']

    # ---------------------------------- IPS -----------------------------------
    def ip_report(self, ip):
        """
        Retrieving IP address reports.
        
        :param ip: a valid IPv4 address in dotted quad notation
        """
        params = {'ip': ip}
        self.__get("post", "ip-address", "report", params=params)

    # --------------------------------- URLS -----------------------------------
    @private
    def url_feed(self, package):
        """
        Retrieve live feed of all URLs submitted to VirusTotal.
        
        :param package: time window to pull reports on all items received during
                         such window
        """
        self.__get("get", "url", "feed", params=params)
    
    def url_report(self, resource, allinfo=False, scan=None):
        """
        Retrieve URL scan reports.
        
        :param resource: scanned URL
        :param allinfo:  return additional information about the file
        :param scan:     (optional) when set to "1" will automatically submit
                          the URL for analysis if no report is found
        """
        params = {'resource': url, 'allinfo': allinfo}
        if scan:
            params['scan'] = str(int(scan))
        self.__get("get", "url", "report", params=params)
        if scan:
            self.json['scan_id']

    def url_scan(self, url):
        """
        Scan an URL.
        
        :param url: URL that should be scanned
        """
        params = {'url': url}
        self.__get("post", "url", "scan", params=params,
            aheaders={'Content-Type': "application/x-www-form-urlencoded"})

