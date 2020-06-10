# -*- coding: UTF-8 -*-
"""Bot using the GhostProjectAPI for bulk-checking email addresses.

"""
from time import sleep
from ...apis import GhostProjectAPI


__all__ = ["GhostProjectBot"]


class GhostProjectBot(GhostProjectAPI):
    """
    Class for requesting information using the GhostProject API.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    def __search(self, email, backoff=1.0):
        try:
            return self.search(email)
        except:
            sleep(backoff)
            backoff *= 1.2
            return self.__search(email, backoff)
    
    def check_from_file(self, emails_path):
        """
        Check a list of emails from a given file.
        
        :param emails_path: path to the file with the list of emails
        :return:            list of all matching emails
        """
        data = {}
        with open(emails_path) as f:
            for email in f:
                data.update(self.__search(email.strip()).get('data', {}))
        return data
    
    def check_from_list(self, *emails):
        """
        Check a list of emails from the given arguments.
        
        :param emails: list of emails
        :return:       list of all matching emails
        """
        data = {}
        for email in emails:
            data.update(self.__search(email.strip()).get('data', {}))
        return data

