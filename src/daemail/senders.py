import locale
import mailbox
import smtplib
import subprocess
import traceback
from   .util import mail_quote, rc_with_signal

class SMTPSender:
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

    def send(self, msg):
        server = self.connect()
        if self.username is not None:
            server.login(self.username, self.password)
        server.send_message(msg)
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


class CommandSender:
    def __init__(self, sendmail):
        self.sendmail = sendmail

    def send(self, msg):
        p = subprocess.run(
            self.sendmail,
            shell  = True,
            input  = bytes(msg),
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
        )
        if p.returncode:
            raise MailCmdError(self.sendmail, p.returncode, p.stdout)

    def about(self):
        yield ('Method', 'command')
        yield ('Command', self.sendmail)


class MboxSender:
    def __init__(self, filename):
        self.filename = filename

    def send(self, msg):
        mbox = mailbox.mbox(self.filename)
        mbox.lock()
        mbox.add(msg)
        mbox.close()

    def about(self):
        yield ('Method', 'mbox')
        yield ('Mbox-File', self.filename)


class TryingSender:
    """
    Tries to send a message via the given sender object, falling back to
    sending to the mbox at ``dead_letter_path`` if that fails
    """

    def __init__(self, sender, dead_letter_path):
        self.sender = sender
        self.dead_letter_path = dead_letter_path

    def send(self, msg):
        msgobj = msg.compile()
        try:
            self.sender.send(msgobj)
        except Exception as e:
            msg.addtext(
                '\nAdditionally, an error occurred while trying to send'
                ' this e-mail:\n\n'
            )
            for k,v in self.sender.about():
                msg.addtext('{}: {}\n'.format(k,v))
            if isinstance(e, MailCmdError):
                msg.addtext('Exit Status: {}\n'.format(rc_with_signal(e.rc)))
                if e.output:
                    msg.addtext('\nOutput:\n')
                    msg.addblobquote(
                        e.output,
                        locale.getpreferredencoding(True),
                        'sendmail-output',
                    )
                else:
                    msg.addtext('\nOutput: none\n')
            else:
                msg.addtext('\nError Traceback:\n')
                msg.addtext(mail_quote(traceback.format_exc()))
            ### TODO: Handle failures here!
            MboxSender(self.dead_letter_path).send(msg.compile())


class MailCmdError(Exception):
    # Raised if the sendmail command returned nonzero
    def __init__(self, sendmail, rc, output):
        self.sendmail = sendmail
        self.rc = rc
        self.output = output

    def __str__(self):
        return '{0.sendmail!r}: command exited with return code {0.rc}'\
               .format(self)
