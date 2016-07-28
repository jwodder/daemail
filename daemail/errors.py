from   __future__ import unicode_literals
import locale
from   .util      import mail_quote, rc_with_signal

class MailCmdError(Exception):
    pass


class InternalMailCmdError(MailCmdError):
    # Raised in reponse to a Python exception
    def __init__(self, msg, cause, mail_cmd):
        self.msg = msg
        self.cause = cause
        self.mail_cmd = mail_cmd

    def update_email(self):
        self.msgaddtext('\nAdditionally, an exception occurred while trying to'
                        ' send this e-mail with ' + repr(self.mail_cmd) +
                        ':\n\n' + mail_quote(str(self.cause)))


class ExternalMailCmdError(MailCmdError):
    # Raised if the mail command returned nonzero
    def __init__(self, msg, mail_cmd, rc, output):
        self.msg = msg
        self.mail_cmd = mail_cmd
        self.rc = rc
        self.output = output

    def update_email(self):
        self.msg.addtext('\nAdditionally, the mail command {0!r} exited with'
                         ' return code {1} when asked to send this e-mail.\n'
                         .format(self.mail_cmd, rc_with_signal(self.rc)))
        if self.output:
            self.msg.addtext('\nMail command output:\n')
            self.msg.addblobquote(self.output,
                                  locale.getpreferredencoding(True),
                                  'sendmail-output')
            self.msg.addtext('\n')
        else:
            self.msg.addtext('\nMail command output: none\n')
