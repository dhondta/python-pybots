# -*- coding: UTF-8 -*-
"""Bot client dedicated to Gotcha.pw.

"""
from ...specific.http import HTTPBot
from ...utils.regex import is_domain, is_email


__all__ = ["GotchaBot"]

URL = "https://gotcha.pw"


class GotchaBot(HTTPBot):
    """
    GotchaBot class for communicating with website Gotcha.

    :param args:     HTTPBot arguments
    :param kwargs:   HTTPBot keyword-arguments
    """
    def __init__(self, *args, **kwargs):
        super(GotchaBot, self).__init__(URL, *args, **kwargs)

    def lookup(self, item):
        """
        Lookup for the given item.
        
        :param item: item to be searched (email or domain)
        """
        if not is_email(item) and not is_domain(item) and \
            not (item[0] == '@' and is_domain(item[1:])):
            raise ValueError("Bad input (should be an email or a domain)")
        if '*' in item:
            raise ValueError("Wildcards are not allowed")
        self.get("/search/{}".format(item))
        content, rows = self.soup.find("div", attrs={'id': "content"}), []
        if content is not None:
            for row in content.find_all("div", attrs={'class': "row"}):
                divs = row.find_all("div")
                rows.append(list(map(lambda x: x.text, divs)))
        return rows
