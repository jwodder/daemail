import smtplib
import subprocess
from   .util import MailCmdError

class SMTPSender(object):
    def __init__(self, from_addr, to_addr, host, port=None,
                       username=None, password=None):
        if username is not None and password is None:
            raise ValueError('Username supplied without password')
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, msgbytes):
        server = self.connect()
        if self.username is not None:
            server.login(self.username, self.password)
        server.sendmail(self.from_addr, [self.to_addr], msgbytes)
        server.quit()

    def connect(self):
        return smtplib.SMTP(self.host, self.port)


class StartTLSSender(SMTPSender):
    def connect(self):
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        return server


class SMTPSSender(SMTPSender):
    def connect(self):
        return smtplib.SMTP_SSL(self.host, self.port)


class CommandSender(object):
    def __init__(self, mail_cmd='sendmail -t'):
        self.mail_cmd = mail_cmd

    def send(self, msgbytes):
        p = subprocess.Popen(self.mail_cmd, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out, _ = p.communicate(msgbytes)
        if p.returncode:
            raise MailCmdError(self.mail_cmd, p.returncode, out)
