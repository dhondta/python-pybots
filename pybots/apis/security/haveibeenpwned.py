# -*- coding: UTF-8 -*-
"""API client dedicated to HaveIBeenPwned?.

"""
from tinyscript import b, hashlib, random, time
from tinyscript.helpers.data.types import *

from ...core.utils.api import *


__all__ = ["HaveIBeenPwnedAPI", "PwnedPasswordsAPI"]


class HaveIBeenPwnedAPI(API):
    """
    Class for communicating with the API of HaveIBeenPwned.
    
    Reference: https://haveibeenpwned.com/API/v3
    Note:      All API methods are rate-limited to 1000 requests/second.

    :param kwargs: JSONBot / API keyword-arguments
    """
    url = "https://haveibeenpwned.com"
    
    def __init__(self, apikey=None, app=None, **kwargs):
        self.__headers = {}
        self.public = apikey is None
        if app:
            self.__headers['User-Agent'] = app
        super(HaveIBeenPwnedAPI, self).__init__(apikey, **kwargs)
    
    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "account":
                email_address(v)
            elif k == "domain":
                domain_name(v)
            elif k == "flags":
                for f in v:
                    if not isinstance(f, bool):
                        raise ValueError("bad boolean value")
    
    @time_throttle(1, requests=1000)
    def _request(self, method, reqpath, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param reqpath: request path
        :param kwargs:  requests.[...](...) parameters
        """
        h = kwargs.pop('aheaders', {})
        h.update(self.__headers)
        retries = kwargs.pop('retries', 3)
        s = super(HaveIBeenPwnedAPI, self)
        s._request("/api/v3" + reqpath, method, aheaders=h, **kwargs)
        if isinstance(self._json, dict) and self._json.get('statusCode'):
            code = self._json['statusCode']
            if code == 429 and retries > 0:
                time.sleep(2)
                kwargs['retries'] = retries - 1
                self._request(method, reqpath, **kwargs)
            else:
                raise APIError(self._json['message'], code)
    
    # Getting all breaches for an account
    @apicall
    @private
    @cache(3600)
    def breachedaccount(self, account, truncate_response=True, domain=None, include_unverified=True):
        """
        Return a list of all breaches a particular account has been involved in.
        
        :param account:            account to be searched for (not case sensitive, trimmed of leading or trailing white
                                    spaces)
        :param truncate_response:  return the full breach model
        :param domain:             filter the result set to only breaches against the domain specified
        :param include_unverified: return breaches that have been flagged as "unverified"
        """
        self._check_apikey("missing hibp-api-key")
        self.__validate(account=account, domain=domain, flags=[truncate_response, include_unverified])
        params = {'truncateResponse': truncate_response, 'includeUnverified': include_unverified}
        if domain:
            params['domain'] = domain
        self._request("get", "/breachedaccount/%s" % account, params=params, aheaders={'hibp-api-key': self._api_key})
    
    # Getting a single breached site
    @apicall
    @cache(86400)
    def breach(self, name):
        """
        Retrieve just a single breach by its "name".
        
        :param name: name of the breach (according to the breach model)
        """
        self.__validate(name=name)
        self._request("get", "/breach/%s" % name)
    
    # Getting all breached sites in the system
    @apicall
    @cache(86400)
    def breaches(self, domain):
        """
        Return the details of each of breach in the system.
        
        NB: A "breach" is an instance of a system having been compromised by an attacker and the data disclosed.
        
        :param domain: filter the result set to only breaches against the domain specified
        """
        self.__validate(domain=domain)
        self._request("get", "/breaches", params={'domain': domain})
    
    # Getting all data classes in the system
    @apicall
    @cache(86400)
    def dataclasses(self):
        """
        Return an alphabetically ordered string array with the data classes.
        
        NB: A "data class" is an attribute of a record compromised in a breach.
        """
        self._request("get", "/dataclasses")
    
    # Getting all pastes for an account
    @apicall
    @private
    @cache(3600)
    def pasteaccount(self, account):
        """
        Return a collection of pastes related to the given account.
        
        :param account: account to be searched for (not case sensitive, trimmed of leading or trailing white spaces)
        
        Attribute   Type    Description
        ----------------------------------------------------------------------------------------------------------------
        Source 	    string  The paste service the record was retrieved from. Values:Pastebin, Pastie, Slexy, Ghostbin,
                             QuickLeak, JustPaste, AdHocUrl, PermanentOptOut, OptOut
        Id 	        string  The ID of the paste as it was given at the source service. Combined with the "Source"
                             attribute, this can be used to resolve the URL of the paste.
        Title 	    string  The title of the paste as observed on the source site. This may be null and if so will be
                             omitted from the response.
        Date 	    date    The date and time (precision to the second) that the paste was posted. This is taken
                             directly from the paste site when this information is available but may be null if no date
                             is published.
        EmailCount 	integer The number of emails that were found when processing the paste. Emails are extracted by
                             using the regular expression:
                              \b+(?!^.{256})[a-zA-Z0-9\.\-_\+]+@[a-zA-Z0-9\.\-_]+\.[a-zA-Z]+\b
        """
        self._check_apikey("missing hibp-api-key")
        self.__validate(account=account)
        self._request("get", "/pasteaccount/%s" % account, aheaders={'hibp-api-key': self._api_key})


class PwnedPasswordsAPI(API):
    """
    Class for communicating with the API of HaveIBeenPwned.
    
    Reference: https://haveibeenpwned.com/API/v3
    Note:      this Web service implements a k-Anonymity model

    :param kwargs: HTTPBot / API keyword-arguments
    """
    url = "https://api.pwnedpasswords.com"
    
    def __init__(self, **kwargs):
        kwargs['kind'] = "http"
        super(PwnedPasswordsAPI, self).__init__(None, **kwargs)
    
    # Searching by range
    @time_throttle(1, requests=1000)
    @apicall
    @cache(3600)
    def count(self, password):
        """
        Search for a password, sending only the 5 first characters of its SHA1 hash to the remote API.
        
        :param password: password to be searched for
        :return:         number of times the password has been encoutered in registered breaches
        """
        h = hashlib.sha1(b(password)).hexdigest().upper()
        self._request("/range/%s" % h[:5])
        hashes = self._response.text.split("\n")
        random.shuffle(hashes)
        for l in hashes:
            hash_suffix, count = l.split(":")
            if h[5:] == hash_suffix:
                return int(count)
        return 0
    
    def counts(self, *passwords):
        """
        Search for pwned passwords.
        
        :param passwords: passwords to be searched for
        """
        r = {}
        for p in passwords:
            r[p] = self.count(p)
        return r

