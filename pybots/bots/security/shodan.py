# -*- coding: UTF-8 -*-
"""Bot client dedicated to Shodan.

"""
from tinyscript.helpers.data.types import is_domain, is_email

from ...apis import ShodanAPI


__all__ = ["ShodanBot"]


class ShodanBot(ShodanAPI):
    """
    ShodanBot class for requesting multiple information using the Shodan API.

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    pass
