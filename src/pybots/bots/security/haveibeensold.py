# -*- coding: UTF-8 -*-
"""Bot using the HaveIBeenSoldAPI for bulk-checking email addresses.

"""
from ...apis import HaveIBeenSoldAPI


__all__ = ["HaveIBeenSoldBot"]


class HaveIBeenSoldBot(HaveIBeenSoldAPI):
    """
    Class for requesting information using the HaveIBeenSold API.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    def __check(self, email):
        try:
            return len(self.check(email)) > 0
        except ValueError:
            return False
    
    def check_from_file(self, emails_path):
        """
        Check a list of emails from a given file.
        
        :param emails_path: path to the file with the list of emails
        :return:            list of all matching emails
        """
        flagged = []
        with open(emails_path) as f:
            for email in f:
                email = email.strip()
                if self.__check(email):
                    flagged.append(email)
        return flagged
    
    def check_from_list(self, *emails):
        """
        Check a list of emails from the given arguments.
        
        :param emails: list of emails
        :return:       list of all matching emails
        """
        flagged = []
        for email in emails:
            email = email.strip()
            if self.__check(email):
                flagged.append(email)
        return flagged

