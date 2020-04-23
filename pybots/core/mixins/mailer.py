# -*- coding: UTF-8 -*-
"""Mixin for sending an email.

This mixin allows to add a sendmail functionality to a Bot, available through a 'send_mail()' method.

"""
import smtplib
from tinyscript.helpers.decorators import *
from tinyscript.helpers.data.types import is_domain, is_email, is_port


__all__ = ["SendMailMixin"]


MSG_TEMPLATE = """From: {from_pers} <{from_mail}>
To: {to_pers} <{to_mail}>
MIME-Version: 1.0
Content-type: text/html
Subject: {subject}

{html}
"""


class SendMailMixin(object):
    @try_and_warn("Mail sending failed", trace=True)
    def send_mail(self, body, **kwargs):
        """
        Send an email to a single receiver.
        
        :param body:   message body (HTML format)
        :param kwargs: email parameters (i.e. mailserver, from, to, ...)
        """
        cfg = getattr(self, "config", {}).get('email', {})
        get = lambda k, d=None: kwargs.get(k, cfg.get(k, d))
        # parameters validation
        subject = get('subject', self.__class__.__name__)
        fm = get('from')
        from_pers, from_mail = fm if isinstance(fm, tuple) and len(fm) == 2 else ("", fm)
        if from_mail is None or not is_email(from_mail):
            raise ValueError("Bad sender email")
        tm = get('to')
        to_pers, to_mail = tm if isinstance(tm, tuple) and len(tm) == 2 else ("", tm)
        if to_mail is None or not is_email(to_mail):
            raise ValueError("Bad receiver email")
        srv = get('mailserver')
        host, port = srv if isinstance(srv, tuple) and len(srv) == 2 else (srv, 25)
        if host is None or not is_domain(host) or not is_port(port):
            raise ValueError("Bad email server parameter")
        # create the email
        msg = MSG_TEMPLATE.format(
            from_pers=from_pers,
            from_mail=from_mail,
            to_pers=to_pers,
            to_mail=to_mail,
            subject=subject,
            html=body,
        )
        # send the email
        srv = smtplib.SMTP(host, port)
        srv.sendmail(from_mail, to_mail, msg)
        srv.quit()
