import mailbox
import smtplib
import subprocess
from   .util import MailCmdError

class SMTPSender(object):
    METHOD = 'SMTP'

    def __init__(self, host, port=None, username=None, password=None):
        if username is not None and password is None:
            raise ValueError('Username supplied without password')
        elif username is None and password is not None:
            raise ValueError('Password supplied without username')
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, msgbytes, from_addr, to_addrs):
        server = self.connect()
        if self.username is not None:
            server.login(self.username, self.password)
        server.sendmail(from_addr, to_addrs, msgbytes)
        server.quit()

    def connect(self):
        return smtplib.SMTP(self.host, self.port)

    def about(self):
        yield ('Method', self.METHOD)
        yield ('Host', self.host)
        yield ('Port', 'default' if self.port is None else self.port)
        if self.username is not None:
            yield ('Authentication', 'yes')
            yield ('Username', self.username)
        else:
            yield ('Authentication', 'no')


class StartTLSSender(SMTPSender):
    METHOD = 'SMTP with STARTTLS'

    def connect(self):
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        return server


class SMTP_SSLSender(SMTPSender):
    METHOD = 'SMTPS'

    def connect(self):
        return smtplib.SMTP_SSL(self.host, self.port)


class CommandSender(object):
    def __init__(self, sendmail):
        self.sendmail = sendmail

    def send(self, msgbytes, _from, _to):
        p = subprocess.Popen(self.sendmail, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out, _ = p.communicate(msgbytes)
        if p.returncode:
            raise MailCmdError(self.sendmail, p.returncode, out)

    def about(self):
        yield ('Method', 'command')
        yield ('Command', self.sendmail)


class MboxSender(object):
    def __init__(self, filename):
        self.filename = filename

    def send(self, msgbytes, _from, _to):
        deadbox = mailbox.mbox(self.filename)
        deadbox.lock()
        deadbox.add(msgbytes)
        deadbox.close()

    def about(self):
        yield ('Method', 'mbox')
        yield ('Mbox-File', self.filename)
