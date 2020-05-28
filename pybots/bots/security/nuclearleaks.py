# -*- coding: UTF-8 -*-
"""Bot dedicated to NuclearLeaks.

"""
from ...apis import NuclearLeaksAPI


__all__ = ["NuclearLeaksBot"]


class NuclearLeaksBot(NuclearLeaksAPI):
    """
    Class for requesting information using the NuclearLeaks API.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    def __check(self, email):
        self.__breaches = {}
        domain = email.split("@")[-1]
        if domain not in self.__breaches.keys():
            self.__breaches[domain] = self.search(domain)
    
    def breaches_from_file(self, path):
        """
        Check a list of emails or domains from a given file.
        
        :param path: path to the file with the list of emails or domains
        :return:     dictionary of all breaches per domain
        """
        with open(path) as f:
            for item in f:
                self.__check(item.strip())
        return self.__breaches
    
    def breaches_from_list(self, *items):
        """
        Check a list of emails or domains from the given arguments.
        
        :param items: list of emails or domain names
        :return:      dictionary of all breaches per domain
        """
        for item in items:
            self.__check(item)
        return self.__breaches

