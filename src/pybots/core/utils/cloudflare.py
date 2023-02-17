# -*- coding: UTF-8 -*-
"""Cloudflare-related functions (e.g. for scraping a security clearance).

"""
import os
from time import sleep, time
try:
    from selenium import webdriver
    enabled = True
except ImportError:
    enabled = False


__all__ = __features__ = ["get_clearance"]


SELENIUM_REQUESTS_KEYS = {'expiry': "expires", 'httpOnly': {'rest': {"httpOnly": True}}}


def get_clearance(url, driver="firefox", executable_paths=None, timeout=30):
    """
    Function getting a URL using Selenium in headless mode (supported for Chrome and Firefox).
    
    :param driver:  selected driver
    :param url:     URL to scrape the clearance from
    :param timeout: timeout for scraping the clearance
    :return:        list of cookies ; empty list if selenium not installed
    """
    if enabled:
        # update the PATH environment variable for the driver
        paths = os.environ['PATH'].split(":")
        for path in (executable_paths or []):
            if os.path.isdir(path) and path not in paths:
                paths.append(path)
        os.environ['PATH'] = ":".join(paths)
        # set headless mode and open a driver instance
        try:
            o = getattr(webdriver, driver.capitalize() + "Options")()
        except AttributeError:
            raise ValueError("Driver '{}' not supported".format(driver))
        o.headless = True
        d = getattr(webdriver, driver.capitalize())(options=o)
        # get the target URL and wait for a security clearance
        d.get(url)
        is_ok = lambda c: "cf_clearance" in [i['name'] for i in c]
        s = time()
        while not is_ok(d.get_cookies()) and time() - s < timeout:
            sleep(1)
        c = d.get_cookies()
        if not is_ok(c):
            raise ValueError("Could not retrieve a Cloudflare security clearance")
        # collect the User-Agent before exiting
        uagent = d.execute_script("return navigator.userAgent;")
        d.quit()
        # set compatible flags for requests
        for cookie in c:
            for k1, k2 in SELENIUM_REQUESTS_KEYS.items():
                if k1 in cookie.keys():
                    if k2:
                        if isinstance(k2, dict):
                            k, v = list(k2.items())[0]
                            cookie[k] = v
                        else:
                            cookie[k2] = cookie[k1] 
                    del cookie[k1]
        return c, uagent
    raise ImportError("Selenium is not installed ; Cloudflare security clearance scrapping disabled.")

