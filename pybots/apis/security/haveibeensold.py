# -*- coding: UTF-8 -*-
"""API client dedicated to HaveIBeenSold.

"""
from tinyscript.helpers.data.types import *

from ...core.utils.api import *


__all__ = ["HaveIBeenSoldAPI"]


class HaveIBeenSoldAPI(API):
    """
    Class for communicating with the API of HaveIBeenSold.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    url = "https://haveibeensold.app"
    
    def __init__(self, **kwargs):
        super(HaveIBeenSoldAPI, self).__init__(None, **kwargs)
        kwargs['random_uagent'] = True
        s = self._session.headers
        s['Content-Type'] = "application/x-www-form-urlencoded"
        s['Origin'] = s['Referer'] = self.url
        s['TE'] = "Trailers"
    
    def __validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "action":
                if v not in ["add", "check", "del"]:
                    raise ValueError("bad action (shoud be add|check|del)")
            elif k == "email":
                email_address(v)
    
    def _request(self, email, action):
        """
        Generic post method.
        
        :param email:  email address
        :param action: action to be performed (add|check|del)
        """
        self.__validate(action=action, email=email)
        s = super(HaveIBeenSoldAPI, self)
        s._request("/api/api.php", "post", random_uagent=True, data={'email': email, 'action': action})
        if self._json.get('status') == "success":
            return self._json.get('data')
        elif self._json.get('status') == "error":
            msg = self._json.get('data')[2:].replace("_", " ").lower()
            raise APIError(msg)
    
    @apicall
    def add(self, email):
        """
        Add a given email to the database.
        
        :param email: email address
        """
        self._request(email, "add")
        self._logger.warning("a confirmation link has been sent to this email")
    
    @apicall
    @cache(3600)
    def check(self, email):
        """
        Return whether the given email was sold.
        
        :param email: email address
        """
        return self._request(email, "check")
    
    @apicall
    def delete(self, email):
        """
        Remove a given email from the database.
        
        :param email: email address
        """
        self._request(email, "del")
        self._logger.warning("a confirmation link has been sent to this email")

