import smtplib
import subprocess
from   .util import MailCmdError

class SMTPSender(object):
    def __init__(self, host, port=None, username=None, password=None):
        if username is not None and password is None:
            raise ValueError('Username supplied without password')
        elif username is None and password is not None:
            raise ValueError('Password supplied without username')
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, msgbytes, from_addr, to_addr):
        server = self.connect()
        if self.username is not None:
            server.login(self.username, self.password)
        server.sendmail(from_addr, [to_addr], msgbytes)
        server.quit()

    def connect(self):
        return smtplib.SMTP(self.host, self.port)


class StartTLSSender(SMTPSender):
    def connect(self):
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        return server


class SMTP_SSLSender(SMTPSender):
    def connect(self):
        return smtplib.SMTP_SSL(self.host, self.port)


class CommandSender(object):
    def __init__(self, mail_cmd=None):
        if mail_cmd is None:
            # Set the default here (instead of in the method signature) so that
            # `main` can pass `None` to the constructor and have it DWIM.
            mail_cmd = 'sendmail -t'
        self.mail_cmd = mail_cmd

    def send(self, msgbytes, _from, _to):
        p = subprocess.Popen(self.mail_cmd, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out, _ = p.communicate(msgbytes)
        if p.returncode:
            raise MailCmdError(self.mail_cmd, p.returncode, out)
