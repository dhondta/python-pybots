#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client dedicated to Gotcha.pw.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["GotchaBot"]


from pybots.specific.http import HTTPBot
from pybots.utils.regex import is_domain, is_email


DOM = "https://gotcha.pw"


class GotchaBot(HTTPBot):
    """
    GotchaBot class for communicating with website Gotcha.
    https://gotcha.pw/

    :param verbose: debug level
    """
    
    def __init__(self, verbose=False):
        super(GotchaBot, self).__init__(DOM, verbose=verbose)

    def lookup(self, item):
        """
        Lookup for the given item.
        
        :param item: item to be searched (email or domain)
        """
        assert is_email(item) or is_domain(item) or (item[0] == '@' and \
            is_domain(item[1:])), "Bad input (should be an email or a domain)"
        assert '*' not in item, "Wildcards cannot be used"
        self.get("/search/{}".format(item))
        content, rows = self.soup.find("div", attrs={'id': "content"}), []
        if content is not None:
            for row in content.find_all("div", attrs={'class': "row"}):
                divs = row.find_all("div")
                rows.append(list(map(lambda x: x.text, divs)))
        return rows
