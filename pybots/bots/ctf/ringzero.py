# -*- coding: UTF-8 -*-
"""Bot client dedicated to RingZer0 CTF website.

  NB: data is available through the attribute 'inputs' which is a dictionary
      whose keys are the tags found on the challenge page

"""
import base64
import os
import re
from tinyscript.helpers.decorators import try_or_die

from ...core.protocols.http import HTTPBot
from ...core.utils.common import *


__all__ = ["RingZer0Bot"]

DOM = "ringzer0team.com"
URL = "https://{}/challenges/".format(DOM)
MSG = re.compile(r'\s*\-+\s(?:BEGIN|END)\s([A-Z]+\s)+\-+\s*', re.I)
IMG = re.compile(r'\s*\-+\s(?:IMAGE)\s\-+\s*', re.I)
CFN = ".cookie"
CKI = re.compile(r'^[a-z0-9]{26}$')
os.environ['NO_PROXY'] = DOM  # disables proxy check by requests module for
                              #  this domain

class RingZer0Bot(HTTPBot):
    """
    RingZer0Bot class mechanizing the process of solving challenges to be
     scripted.

    :param cid:      challenge identifier
    :param cookie:   PHP session ID cookie
    :param args:     HTTPBot arguments
    :param kwargs:   HTTPBot keyword-arguments
    
    Note:
      The cookie can also be left None in the input arguments and be loaded from
       a .cookie file. It can be saved as "PHPSESSID=..." or simply "...".
    
    Example usage:
    
      from pybots import RingZer0Bot
      
      with RingZer0Bot(5, "...your-cookie...") as bot:
          # do some computation with bot.inputs here
          # NOTE: bot.inputs is a dictionary containing input values from
          #        challenge's source ; e.g. 'message' or 'image' for this bot
          bot.answer = computed_value
          # now, while exiting the context, the flag will be displayed if the
          #  answer was correct (or a message if wrong)
    """
    def __init__(self, cid, cookie=None, *args, **kwargs):
        super(RingZer0Bot, self).__init__("{}{}".format(URL, cid), *args,
                                          **kwargs)
        self.answer = None
        self.cid = cid
        # set the cookie
        if cookie is None:
            with open(CFN, 'r+') as f:
                cookie = f.read().strip()
        if not CKI.match(cookie):
            raise Exception
        if not cookie.startswith("PHPSESSID="):
            cookie = "PHPSESSID={}".format(cookie)
        self._set_cookie(cookie)

    @try_or_die("No CSRF token found", extra_info="response")
    def __get_csrf(self):
        """
        Retrieve the CSRF token from the page.

        :post: self.csrf populated
        """
        c = self.soup.find('input', {'name': 'csrf'}).get('class')[0]
        # FIXME: handle this in a more robust way
        for s in self.soup.find_all('script'):
            l = s.text
            if c in l:
                self.csrf = l.split(";")[0].split("=")[1].strip(" '\"")
                break
        self.logger.debug("CSRF token found: {}".format(self.csrf))
        return self

    @try_or_die("Fatal error while parsing downloads", extra_info="response")
    def __get_downloads(self):
        """
        Retrieve the downloads from the challenge page.
        """
        self.downloads = []
        wrapper = self.soup.find('div', {"class" : "challenge-wrapper"})
        for div in wrapper.find_all('div', {"class" : "download"}):
            href = div.find('a').attrs['href']
            self.retrieve(href)
            self.downloads.append(os.path.basename(href))
        if len(self.downloads) > 0:
            self.logger.info(" - Downloads: {}"
                             .format(", ".join(self.downloads)))
        return self

    @try_or_die("No flag found", extra_info="response")
    def __get_flag(self):
        """
        Retrieves the flag to be submitted from the challenge page.

        :post: self.flag populated
        """
        try:
            self.flag = self.soup.find('div', {"class" : "alert-info"}).text
        except AttributeError:
            self.flag = self.soup.find('div', {"class" : "flag"}).text
        self.logger.info("Flag found: {}".format(self.flag))

    @try_or_die("Fatal error while parsing information", extra_info="response")
    def __get_info(self):
        """
        Retrieve the flag to be submitted from the challenge page.

        :post: self.flag populated
        """
        self.logger.info("Challenge information:")
        title = self.soup.find_all('h4')[0].text.strip()
        self.logger.info(" - Title    : {}".format(title))
        if "Website Login" in title:
            self.logger.warn("Please login and/or write your CURRENT session"
                             " cookie in '{}' before.".format(CFN))
            HTTPBot.shutdown(code=0)
        statement = '\n'.join(s.text for s in self.soup \
            .find('div', {"class" : "challenge-wrapper"}).find_all('strong'))
        if len(statement) > 0:
            self.logger.info(" - Statement: {}".format(statement))
        return self

    @try_or_die("Fatal error while parsing inputs", extra_info="response")
    def __get_inputs(self):
        """
        Retrieve the inputs to be processed from the main page contained in
         the <div class="message"> tags.

        :post: self.inputs populated
        """
        self.inputs = {}
        for br in self.soup.find_all("br"):
            br.replace_with("\n")
        for div in self.soup.find_all('div', {"class" : "message"}):
            if div.attrs['class'] == "download":
                print(div.find_all('a')[0].attrs['href'])
            msg = div.text
            # try to match "----- BEGIN|END ... -----" tags
            match = MSG.match(msg)
            if match is not None:
                tag = ' '.join(MSG.match(msg).group().split()[2:-1]).upper()
                msg = MSG.sub("", msg).encode('utf-8')
                self.inputs[tag] = msg
            else:
                # try to match on "----- IMAGE -----" tags
                match = IMG.match(msg)
                if match is not None:
                    tag = 'IMAGE'
                    src = div.find('img').attrs['src']
                    if src.startswith('data:image'):
                        head, data = src.split(";")
                        ext = head.split("/")[1]
                        enc, data = data.split(",")
                        if enc == 'base64':
                            msg = ".image." + ext
                            with open(msg, 'wb') as f:
                                f.write(base64.b64decode(data))
                        else:
                            self.logger.warn("An image was not decoded")
                            continue
                    else:
                        _, ext = os.path.splitext(src)
                        msg = ".image" + ext
                        self.retrieve(src, msg)
                    self.inputs[tag] = msg
                else:
                    self.logger.warn("Message block found but nothing parsed")
                    continue
            self.logger.debug("{} found: {}".format(tag, msg))
        return self

    @try_or_die("Submission failed", extra_info="response")
    def __get_points(self):
        """
        Get the notification with the total of earned points or an alert.
        """
        p = None
        try:
            p = self.soup.find('div', {"class" : "alert-success"}).text
        except AttributeError:
            p = self.soup.find('div', {"class" : "alert-danger"}).text
        if p:
            self.logger.info(p)
        else:
            self.logger.debug("No feedback notification found !")

    @try_or_die("No 'answer' attribute set ; please define it")
    def postamble(self):
        """
        Custom postamble for submitting the flag and earning the points.
        """
        if self.answer is not None:
            self.get("/{}".format(self.answer))
        else:
            raise AttributeError
        self.__get_flag()
        # then submit the flag (twice, regetting the CSRF token between both
        #  requests) to complete the challenge
        data = {'flag': self.flag, 'id': self.cid, 'csrf': self.csrf,
                'check': True}
        addheaders = {'Referer': self.url}
        self.post(data=data, addheaders=addheaders)
        self.__get_csrf()
        self.post(data=data, addheaders=addheaders)
        self.__get_points()

    @try_or_die("Could not retrieve challenge information")
    def preamble(self):
        """
        Custom preamble for getting the challenge information.
        """
        # get the challenge page and retrieve CSRF token and message
        self.get().__get_info().__get_downloads().__get_csrf().__get_inputs()

