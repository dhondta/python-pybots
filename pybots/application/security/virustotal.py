# -*- coding: UTF-8 -*-
"""Bot client dedicated to VirusTotal API.

"""
from tinyscript.helpers.types import *

from ...specific.json import JSONBot
from ...utils.common import *


__all__ = ["VirusTotalBot"]

DOM = "https://www.virustotal.com"
REQ = "/vtapi/v2/"
RES = {
    'file': ["behaviour", "download", "scan", "rescan", "report"],
    'url': ["scan", "report"],
    'domain': ["report"],
    'ip-address': ["report"],
    'comments': ["put"],
}


def private(f):
    def _wrapper(self, *args, **kwargs):
        if self.public:
            raise APIError("Only available in the private API")
        return f(self, *args, **kwargs)
    return _wrapper


def valid_hash(f):
    if not (is_md5(f) or is_sha1(f) or is_sha256(f)):
        raise ValueError("Not a valid resource hash")


class VirusTotalBot(JSONBot):
    """
    VirusTotalBot class for communicating with the API v2 of VirusTotal.
    
    Reference: https://www.virustotal.com/es/documentation/public-api/

    :param api_key: API key
    :param args:   JSONBot arguments
    :param kwargs: JSONBot keyword-arguments
    """
    def __init__(self, api_key, public=True, verbose=False):
        super(VirusTotalBot, self).__init__(DOM, verbose)
        self.api_key = api_key
        self.public = public
        self._disable_time_throttling = not public

    @time_throttle(60, 4)
    def __get(self, method, restype, action, extra=None, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param restype: resource type (host, url, domain, ip, comments)
        :param action:  action item to be processed for the given resource
        :param extra:   additional URL subpath to be used
        """
        if method not in ["get", "post"]:
            raise ValueError("Method should be 'get' or 'post'")
        if restype not in RES.keys():
            raise ValueError("Bad resource type")
        if action not in RES[restype]:
            raise ValueError("Bad action (given the selected resource type)")
        url = REQ + restype + "/" + action
        if extra:
            url += "/" + extra
        url = kwargs.pop('override_url', None) or url
        params = kwargs.pop('params', {})
        params['apikey'] = self.api_key
        getattr(self, method)(url, params=params, **kwargs)

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
