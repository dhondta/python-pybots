#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client for managing bins on https://postb.in.

"""
import random
import re
from datetime import datetime

from ...core.protocols.http import JSONBot


__all__ = ["PostBinBot"]


class PostBinBot(JSONBot):
    _bins = []
    
    # Bin representation, parsed through the JSON received from the API
    class Bin(object):
        _requests = []
        
        # Request representation, parsed through the JSON received from the API
        class Request(object):
            def __init__(self, json):
                self.__dict__.update(json)
    
        def __init__(self, json):
            self.id      = json["binId"]
            self.created = json["now"]
            self.expires = json["expires"]
        
        def pop(self):
            """
            Get and remove the first request from the bin.
            
            :param reqid: request identifier
            :return:      Request object popped
            """
            self.bot.get("/api/bin/{}/req/shift".format(self.id))
            if self.bot.response.status_code == 200:
                return PostBinBot.Bin.Request(self.bot.json)
        
        def request(self, reqid):
            """
            Get a specific request from the bin.
            
            :param reqid: request identifier
            :return:      Request object selected
            """
            if not hasattr(self, "bot"):
                return
            self.bot.get("/api/bin/{}/req/{}".format(self.id, reqid))
            if self.bot.response.status_code == 200:
                return PostBinBot.Bin.Request(self.bot.json)
        
        @property
        def expired(self):
            return int(datetime.now().timestamp() * 1000) >= self.expires
    
    def __init__(self, *args, **kwargs):
        self.__clean = kwargs.pop("clean", False)
        super(PostBinBot, self).__init__("https://postb.in/", *args, **kwargs)
    
    def bin(self, binid):
        """
        Select a given bin from the list.
        
        :param binid: bin identifier
        :return:      Bin object selected or None if it does not exist
        """
        if not re.search(r"^\d+(\-\d+)*$", binid):
            return
        for b in self._bins:
            if b.id == binid:
                if b.expired:
                    delattr(b, "bot")
                    self._bins.remove(b)
                    self.logger.debug("Bin '{}' expired".format(b.id))
                return b
        self.get("/api/bin/{}".format(binid))
        if self.response.status_code == 200:
            b = PostBinBot.Bin(self.json)
            b.bot = self
            self._bins.append(b)
            return b
    
    def clear(self):
        """
        Clear the complete list of bins.
        """
        for b in self._bins:
            self.delete(b.id)
    
    def close(self):
        """
        Clear the bins before leaving.
        """
        if self.__clean:
            self.clear()
        super(PostBinBot, self).close()
    
    def create(self):
        """
        Create a new bin in the list.

        :return:      Bin object created
        """
        self.post("/api/bin")
        if self.response.status_code == 201:
            b = PostBinBot.Bin(self.json)
            b.bot = self
            self._bins.append(b)
            return b
    
    def delete(self, binid):
        """
        Remove the given bin from the list.

        :param binid: bin identifier
        """
        self.pop(binid)
    
    def pick(self):
        """
        Pick a random bin from the list.
        
        :return: random Bin object
        """
        return random.choice(self._bins)
    
    def pop(self, binid):
        """
        Pop the given bin from the list.

        :param binid: bin identifier
        :return:      Bin object removed frmo the list
        """
        b = self.bin(binid)
        if not b.expired:
            self.delete("/api/bin/{}".format(b.id))
        else:
            self.logger.debug("bin was already expired")
        delattr(b, "bot")
        self._bins.remove(b)
        return b
    
    @property
    def binids(self):
        return [b.id for b in self._bins]

