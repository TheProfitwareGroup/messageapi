#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from time import sleep
import smtplib
from urllib import urlopen, quote

from . import AbstractSenderPlugin


# Defaults
SMSC_POST = False
SMSC_HTTPS = False
SMSC_CHARSET = 'utf-8'

# SMSC SMTP
SMTP_FROM = 'api@smsc.ru'
SMTP_SERVER = 'send.smsc.ru'
SMTP_LOGIN = ''
SMTP_PASSWORD = ''


class SMSCPlugin(AbstractSenderPlugin):
    """SMSC interface"""

    def __init__(self, **kwargs):
        super(SMSCPlugin, self).__init__(**kwargs)

        self['smsc_post'] = self.get('smsc_post', SMSC_POST)
        self['smsc_https'] = self.get('smsc_https', SMSC_HTTPS)
        self['smsc_charset'] = self.get('smsc_charset', SMSC_CHARSET)

        self['smtp_from'] = self.get('smtp_from', SMTP_FROM)
        self['smtp_server'] = self.get('smtp_server', SMTP_SERVER)
        self['smtp_login'] = self.get('smtp_login', SMTP_LOGIN)
        self['smtp_password'] = self.get('smtp_password', SMTP_PASSWORD)

        # SMSC Login and Password are required
        assert self['login']
        assert self['password']

    def send(self, **kwargs):
        phones = kwargs.pop('phones')
        message = kwargs.pop('message')
        return self.send_sms(phones, message, **kwargs)

    def send_sms(self, phones, message, translit=0, time='', sms_id=0, sms_format=0, sender=False, query=''):
        formats = ['flash=1', 'push=1', 'hlr=1', 'bin=1', 'bin=2', 'ping=1']

        m = self._smsc_send_cmd('send', 'cost=3&phones=' + quote(phones) + '&mes=' + quote(message) +
                                '&translit=' + str(translit) + '&id=' + str(sms_id) +
                                ('&' + formats[sms_format - 1] if sms_format > 0 else '') +
                                ('&sender=' + quote(str(sender)) if sender else '') +
                                ('&time=' + quote(time) if time else '') +
                                ('&' + query if query else ''))

        return m

    def send_sms_mail(self, phones, message, translit=0, time='', sms_id=0, sms_format=0, sender=''):
        smtp_server, smtp_login, smtp_password, smtp_from, smsc_charset, smsc_login, smsc_password = \
            [self.get(i) for i in (
                'smtp_server', 'smtp_login', 'smtp_password', 'smtp_from', 'smsc_charset', 'login', 'password'
            )]

        server = smtplib.SMTP(smtp_server)

        if smtp_login:
            server.login(smtp_login, smtp_password)

        server.sendmail(smtp_from, 'send@send.smsc.ru',
                        'Content-Type: text/plain; charset=' + smsc_charset + '\n\n' +
                        smsc_login + ':' + smsc_login + ':' + str(sms_id) + ':' + time + ':' +
                        str(translit) + ',' + str(sms_format) + ',' + sender + ':' + phones + ':' + message)
        server.quit()

    def get_sms_cost(self, phones, message, translit=0, sms_format=0, sender=False, query=''):
        formats = ['flash=1', 'push=1', 'hlr=1', 'bin=1', 'bin=2', 'ping=1']

        m = self._smsc_send_cmd('send', 'cost=1&phones=' + quote(phones) + '&mes=' + quote(message) + \
                                ('&sender=' + quote(str(sender)) if sender else '') +
                                '&translit=' + str(translit) +
                                ('&' + formats[sms_format - 1] if sms_format > 0 else '') +
                                ('&' + query if query else ''))

        return m

    def get_status(self, sms_id, phone, check_all=0):
        m = self._smsc_send_cmd('status', 'phone=' + quote(phone) + '&id=' + str(sms_id) + '&all=' + str(check_all))

        if check_all and len(m) > 9 and (len(m) < 14 or m[14] != 'HLR'):
            m = (','.join(m)).split(',', 8)

        return m

    def get_balance(self):
        m = self._smsc_send_cmd('balance')  # (balance) или (0, -error)

        return False if len(m) > 1 else m[0]

    def _smsc_send_cmd(self, cmd, arg=''):
        smsc_https, smsc_login, smsc_password, smsc_charset, smsc_post = \
            [self.get(i) for i in (
                'smsc_https', 'login', 'password', 'smsc_charset', 'smsc_post'
            )]
        url = ('https' if smsc_https else 'http') + '://smsc.ru/sys/' + cmd + '.php'
        arg = 'login=' + quote(smsc_login) + '&psw=' + quote(smsc_password) + \
              '&fmt=1&charset=' + smsc_charset + ('&' + arg if arg else '')

        i = 0
        ret = ''

        while ret == '' and i < 3:
            if i > 0:
                sleep(2)

            if i == 2:
                url = url.replace('://smsc.ru/', '://www2.smsc.ru/')

            try:
                if smsc_post or len(arg) > 2000:
                    data = urlopen(url, arg.encode(smsc_charset))
                else:
                    data = urlopen(url + '?' + arg)

                ret = str(data.read())
            except Exception:
                ret = ''

            i += 1

        if ret == '':
            ret = ','

        return ret.split(',')
