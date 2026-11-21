"""The mail of the application: sent by SMTP."""

__all__ = ("AppMailUnit",)

from ingot_mail.contrib.aiosmtplib import AiosmtplibMailer
from ingot_mail.mail import MailUnit
from ingots.puer import Slot


class AppMailUnit(MailUnit):
    mailer = Slot(AiosmtplibMailer)
