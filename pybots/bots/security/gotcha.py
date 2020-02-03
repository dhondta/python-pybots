# -*- coding: UTF-8 -*-
"""Bot client dedicated to Gotcha.pw.

"""
from tinyscript.helpers.data.types import is_domain, is_email

from ...core.protocols.http import HTTPBot
from ...core.utils.api import *


__all__ = ["GotchaBot"]

URL = "https://gotcha.pw"


class GotchaBot(HTTPBot, API):
    """
    GotchaBot class for communicating with website Gotcha.

    :param args:     HTTPBot arguments
    :param kwargs:   HTTPBot keyword-arguments
    """
    def __init__(self, *args, **kwargs):
        API.__init__(self, "", **kwargs)
        HTTPBot.__init__(self, URL, *args, **kwargs)
    
    @apicall
    @cache(300)
    def lookup(self, *items):
        """
        Lookup for given items.
        
        :param items: items to be searched (email or domain)
        """
        rows = []
        for item in items:
            if not is_email(item) and not is_domain(item) and \
                not (item[0] == '@' and is_domain(item[1:])):
                raise ValueError("Bad input (should be an email or a domain)")
            if '*' in item:
                raise ValueError("Wildcards are not allowed")
            self.get("/search/{}".format(item))
            content = self.soup.find("div", attrs={'id': "content"})
            if content is not None:
                for row in content.find_all("div", attrs={'class': "row"}):
                    divs = row.find_all("div")
                    rows.append(list(map(lambda x: x.text, divs)))
        return rows
