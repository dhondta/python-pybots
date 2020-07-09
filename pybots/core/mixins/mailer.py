# -*- coding: UTF-8 -*-
"""Mixin for sending an email.

This mixin allows to add a sendmail functionality to a Bot, available through a 'send_mail()' method.

"""
import mimetypes
import os
import smtplib
from bs4 import BeautifulSoup
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tinyscript.helpers.decorators import *
from tinyscript.helpers.data.types import is_domain, is_email, is_file, is_port


__all__ = ["SendMailMixin"]


SECURITY = {465: "ssl", 587: "starttls"}
SERVERS = {
    'aol.com':        ("smtp.aol.com", 465),
    'gmail.com':      ("smtp.gmail.com", 587),
    'gmx.com':        ("smtp.gmx.com", 465),
    'hotmail.com':    ("smtp.live.com", 465),
    'hubspot.com':    ("smtp.hubspot.com", 587),
    'mail.com':       ("smtp.mail.com", 465),
    'microsoft.com':  ("smtp.office365.com", 587),
    'outlook.com':    ("smtp.office365.com", 587),
    'pepipost.com':   ("smtp.pepipost.com", 587),
    'protonmail.com': ("smtp.protonmail.com", 465),
    'yahoo.com':      ("smtp.mail.yahoo.com", 587),
    'zoho.com':       ("smtp.zoho.com", 465),
}


@applicable_to("SocketBot", "WebBot")
class SendMailMixin(object):
    @try_and_warn("Mail sending failed", trace=True)
    def send_mail(self, body, *attachments, **kwargs):
        """
        Send an email to a single receiver.
        
        :param body:   message body (HTML format)
        :param kwargs: email parameters (i.e. mailserver, from, to, ...)
        """
        subject = self._get_option('mailer', 'subject', self.__class__.__name__, kwargs)
        tm = self._get_option('mailer', 'to', None, kwargs)
        fm = self._get_option('mailer', 'from', None, kwargs)
        sec = self._get_option('mailer', 'security', "unencrypted", kwargs)
        srv = self._get_option('mailer', 'mailserver', None, kwargs)
        auth = self._get_option('mailer', 'auth', None, kwargs)
        auth_user, auth_pswd = (None, None) if auth is None else auth if len(auth) == 2 else (fm, auth)
        domain = (auth_user or fm).split("@")[-1]
        # parameters validation
        if not is_email(fm):
            raise ValueError("Bad sender email")
        if not is_email(tm):
            raise ValueError("Bad receiver email")
        if srv is None and domain in SERVERS.keys():
            host, port = SERVERS[domain]
            if port in SECURITY.keys():
                sec = SECURITY[port]
        else:
            host, port = srv if isinstance(srv, tuple) and len(srv) == 2 else (srv, 25)
        if host is None or not is_domain(host) or not is_port(port):
            raise ValueError("Bad email server host or port")
        for path in attachments:
            if not is_file(path):
                raise ValueError("Attachment '%s' does not exist" % path)
        # create the email
        msg = MIMEMultipart()
        msg['From'] = fm
        msg['To'] = tm
        msg['Subject'] = subject
        msg.attach(MIMEText(body, "html" if bool(BeautifulSoup(body, "html.parser").find()) else "plain"))
        # see: https://docs.python.org/3.4/library/email-examples.html
        for path in attachments:
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split("/", 1)
            cls = globals().get("MIME" + maintype.capitalize())
            with open(path, 'rb') as f:
                if cls:
                    submsg = cls(f.read(), _subtype=subtype)
                else:
                    submsg = MIMEBase(maintype, subtype)
                    submsg.set_payload(f.read())
                    encoders.encode_base64(submsg)
            # Set the filename parameter
            submsg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
            msg.attach(submsg)
        # send the email
        session = getattr(smtplib, "SMTP_SSL" if sec == "ssl" else "SMTP")(host, port)
        if sec == "starttls":
            session.starttls()
        if auth:
            session.login(auth_user, auth_pswd)
        session.sendmail(fm, tm, msg.as_string())
        session.quit()
        self.logger.error("Mail sent to %s" % tm)

