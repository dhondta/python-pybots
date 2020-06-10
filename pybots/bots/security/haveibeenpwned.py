# -*- coding: UTF-8 -*-
"""Bot using HaveIBeenPwned for bulk-checking domain breaches and pwned passwords.

"""
from ...apis import HaveIBeenPwnedAPI, PwnedPasswordsAPI


__all__ = ["HaveIBeenPwnedBot", "PwnedPasswordsBot"]


class HaveIBeenPwnedBot(HaveIBeenPwnedAPI):
    """
    Class for requesting information using the HaveIBeenPwned? API.
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    def __check(self, email):
        self.__breaches = {}
        domain = email.split("@")[-1]
        if domain not in self.__breaches.keys():
            self.__breaches[domain] = self.breaches(domain)
    
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


class PwnedPasswordsBot(PwnedPasswordsAPI):
    """
    Class for requesting information using the PwnedPasswords API (part of HaveIBeenPwned).
    
    :param kwargs: JSONBot / API keyword-arguments
    """
    def check_from_file(self, passwords_path):
        """
        Check a list of passwords from a given file.
        
        :param passwords_path: path to the file with the list of passwords
        :return:               list of all pwned passwords
        """
        pwned = []
        with open(passwords_path) as f:
            for p in f:
                password = p.strip()
                if self.count(password) > 0:
                    pwned.append(password)
        return pwned
    
    def check_from_list(self, *passwords):
        """
        Check a list of passwords from the given arguments.
        
        :param passwords: list of passwords
        :return:          list of all pwned passwords
        """
        pwned = []
        for p in passwords:
            password = p.strip()
            if self.count(password) > 0:
                pwned.append(password)
        return pwned

