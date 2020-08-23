# -*- coding: UTF-8 -*-
"""Mixin for sending an email.

This mixin allows to add a sendmail functionality to a Bot, available through a 'send_mail()' method.

"""
from tinyscript.helpers.decorators import *
from tinyscript.helpers.notify import send_mail


__all__ = ["SendMailMixin"]


@applicable_to("SocketBot", "WebBot")
class SendMailMixin(object):
    @try_and_warn("Mail sending failed", trace=True)
    def send_mail(self, body, *attachments, **kwargs):
        """
        Send an email to a single receiver.
        
        :param body:   message body (HTML format)
        :param kwargs: email parameters (i.e. mailserver, from, to, ...)
        """
        options = {}
        subject = self._get_option('mailer', 'subject', self.__class__.__name__, kwargs)
        tm = self._get_option('mailer', 'to', None, kwargs)
        fm = self._get_option('mailer', 'from', None, kwargs)
        options['server'] = self._get_option('mailer', 'mailserver', None, kwargs)
        options['security'] = self._get_option('mailer', 'security', "unencrypted", kwargs)
        options['auth'] = self._get_option('mailer', 'auth', None, kwargs)
        send_mail(fm, tm, subject, body, *attachments, **options)
        self.logger.error("Mail sent to %s" % tm)

