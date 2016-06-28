#!/usr/bin/python
from   __future__             import print_function, unicode_literals
import argparse
from   datetime               import datetime
import email.charset
from   email.encoders         import encode_base64
from   email.message          import Message
from   email.mime.application import MIMEApplication
from   email.mime.multipart   import MIMEMultipart
from   email.mime.text        import MIMEText
import locale
import platform
import os
import re
import signal
import subprocess
import sys
import traceback
from   daemon                 import DaemonContext  # python-daemon

if sys.version_info[0] == 2:
    from pipes import quote
else:
    from shlex import quote

__version__ = '0.3.0'

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

utf8qp = email.charset.Charset('utf-8')
utf8qp.body_encoding = email.charset.QP

class CommandMailer(object):
    def __init__(self, sender=None, to=None, failure_only=False, nonempty=False,
                 mail_cmd=None, no_stdout=False, no_stderr=False, split=False,
                 encoding=None, err_encoding=None, utc=False, mime_type=None):
        self.sender = sender
        self.to = to
        self.failure_only = failure_only
        self.nonempty = nonempty
        self.mail_cmd = mail_cmd
        self.no_stdout = no_stdout
        self.no_stderr = no_stderr
        self.split = split or mime_type is not None
        self.encoding = encoding
        self.err_encoding = err_encoding
        self.utc = utc
        self.mime_type = mime_type
        if self.to is None:
            self.to = os.getlogin()
        if self.mail_cmd is None:
            self.mail_cmd = 'sendmail -t'
        if self.encoding is None:
            self.encoding = locale.getpreferredencoding(True)
        if self.err_encoding is None:
            self.err_encoding = self.encoding

    def run(self, command, *args):
        cmdstring = ' '.join(map(quote, (command,) + args))
        msg = DraftMessage()
        if self.sender is not None:
            msg.headers['From'] = self.sender
        msg.headers['To'] = self.to
        msg.headers['User-Agent'] = USER_AGENT
        try:
            results = self.subcmd(command, *args)
        except Exception:
            msg.headers['Subject'] = '[ERROR] ' + cmdstring
            msg.addtext('An error occurred while attempting to run the command:'
                        '\n' + mail_quote(traceback.format_exc()))
        else:
            if results["rc"] == 0 and (self.failure_only or
                    self.nonempty and not (results["stdout"] or
                                           results["stderr"])):
                return
            if results["rc"] == 0:
                msg.headers['Subject'] = '[DONE] ' + cmdstring
            else:
                msg.headers['Subject'] = '[FAILED] ' + cmdstring
            results["rc"] = rc_with_signal(results["rc"])
            msg.addtext('Start Time:  {start}\n'
                        'End Time:    {end}\n'
                        'Exit Status: {rc}\n'.format(**results))
            # An empty byte string is always an empty character string and vice
            # versa, right?
            if results["stdout"]:
                msg.addtext('\nOutput:\n')
                if self.mime_type is not None:
                    msg.addmimeblob(results["stdout"], self.mime_type, 'stdout')
                else:
                    msg.addblobquote(results["stdout"], self.encoding, 'stdout')
                msg.addtext('\n')
            elif results["stdout"] is not None:
                msg.addtext('\nOutput: none\n')
            if results["stderr"]:
                # If stderr was captured separately but is still empty, don't
                # bother saying "Error Output: none".
                msg.addtext('\nError Output:\n')
                msg.addblobquote(results["stderr"], self.err_encoding, 'stderr')
                msg.addtext('\n')
        msg.send(self.mail_cmd)

    def subcmd(self, command, *args):
        params = {}
        if self.split or self.no_stdout or self.no_stderr:
            params = {
                "stdout": None if self.no_stdout else subprocess.PIPE,
                "stderr": None if self.no_stderr else subprocess.PIPE,
            }
        else:
            params = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        if self.utc:
            start = datetime.utcnow().isoformat() + 'Z'
        else:
            start = datetime.now().isoformat()
        p = subprocess.Popen((command,) + args, **params)
        # The command's output is all going to be in memory at some point
        # anyway, so why not start with `communicate`?
        out, err = p.communicate()
        if self.utc:
            end = datetime.utcnow().isoformat() + 'Z'
        else:
            end = datetime.now().isoformat()
        return {
            "rc": p.returncode,
            "start": start,
            "end": end,
            "stdout": out,
            "stderr": err,
            #"pid": p.pid,
        }


class DraftMessage(object):
    def __init__(self):
        self.headers = {}
        self._attached = []  # list of MIMEBAse objects
        self._trailing = ''

    def addtext(self, txt):
        self._trailing += txt

    def _endtext(self):
        if self._trailing:
            # In case of `addtext, _endtext, addtext, _endtext`:
            if self._attached and isinstance(self._attached[-1], MIMEText):
                last = self._attached[-1]
                last.set_payload(mime_text(last) + self._trailing, utf8qp)
            else:
                msg = MIMEText('', _charset=None)
                # No, `utf8qp` cannot be passed to MIMEText's constructor, as
                # it seems to expect a string (in Python 2.7, at least).
                msg.set_payload(self._trailing, utf8qp)
                self._attached.append(msg)
            self._trailing = ''

    def addblobquote(self, blob, encoding, filename):
        try:
            txt = blob.decode(encoding)
        except UnicodeDecodeError:
            self._endtext()
            attach = MIMEApplication(blob)
            attach.add_header('Content-Disposition', 'inline',
                              filename=filename)
            self._attached.append(attach)
        else:
            self.addtext(mail_quote(txt))

    def addmimeblob(self, blob, mimetype, filename):
        attach = Message()
        attach['Content-Type'] = mimetype
        attach.add_header('Content-Disposition', 'inline', filename=filename)
        attach.set_payload(blob)
        encode_base64(attach)
        self._endtext()
        self._attached.append(attach)

    def compile(self):
        self._endtext()
        if not self._attached:
            msg = MIMEText('', _charset=None)
        elif len(self._attached) == 1 and \
                isinstance(self._attached[0], MIMEText):
            # Copy the payload so that we don't set any headers on the
            # attachment itself, which would cause problems if `compile` is
            # later called again after more attachments have been added
            msg = MIMEText('', _charset=None)
            msg.set_payload(mime_text(self._attached[0]), utf8qp)
        else:
            msg = MIMEMultipart(_subparts=self._attached)
        for k,v in self.headers.items():
            msg[k] = v
        return bytes(msg)
        # `bytes` is an alias for `str` in Python 2.6 and 2.7

    def send(self, mail_cmd):
        msg = self.compile()
        try:
            p = subprocess.Popen(mail_cmd, shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            out, _ = p.communicate(msg)
        except Exception as e:
            raise InternalMailCmdError(self, e, mail_cmd)
        if p.returncode:
            raise ExternalMailCmdError(self, mail_cmd, p.returncode, out)


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


def mail_quote(s):
    s = '> ' + re.sub(r'(\r(\n|(?!\n))|\n)(?=.)', '\n> ', s, flags=re.S)
    if not s.endswith("\n"):
        s += "\n"
    return s

def mime_text(msg):
    # Even if you say `decode=True`, get_payload still returns a `bytes` object
    return msg.get_payload(decode=True).decode('utf-8')

def rc_with_signal(rc):
    if rc < 0:
        # cf. <http://stackoverflow.com/q/2549939/744178>
        signames = [k for k,v in vars(signal).items()
                      if k.startswith('SIG') and v == -rc]
        if signames:
            return '{} ({})'.format(rc, ', '.join(signames))
    return str(rc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chdir', metavar='DIR', default=os.getcwd(),
                        help="Change to this directory before running")
    parser.add_argument('-D', '--dead-letter', metavar='FILE',
                        default='dead.letter',
                        help="Append undeliverable mail to this file")
    parser.add_argument('-e', '--encoding',
                        help='Set encoding of stdout and stderr')
    parser.add_argument('-E', '--err-encoding', help='Set encoding of stderr',
                        metavar='ENCODING')
    parser.add_argument('-f', '--from', '--sender', dest='sender',
                        help='From: address of e-mail')
    parser.add_argument('-F', '--failure-only', action='store_true',
                        help='Only send e-mail if command returned nonzero')
    parser.add_argument('-l', '--logfile',
                        help='Append unrecoverable errors to this file')
    parser.add_argument('-m', '--mail-cmd', default='sendmail -t',
                        metavar='COMMAND', help='Command for sending e-mail')
    parser.add_argument('-M', '--mime-type',
                        help='Send output as attachment with given MIME type')
    parser.add_argument('-n', '--nonempty', action='store_true',
                        help='Only send e-mail if there was output or failure')
    parser.add_argument('--no-stdout', action='store_true',
                        help="Don't capture stdout")
    parser.add_argument('--no-stderr', action='store_true',
                        help="Don't capture stderr")
    parser.add_argument('--split', action='store_true',
                        help='Capture stdout and stderr separately')
    parser.add_argument('-t', '--to', '--recipient', '--rcpt',
                        help='To: address of e-mail', metavar='RECIPIENT')
    parser.add_argument('-V', '--version', action='version',
                                           version='daemail ' + __version__)
    parser.add_argument('-Z', '--utc', action='store_true',
                        help='Use UTC timestamps')
    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    mailer = CommandMailer(
        encoding=args.encoding,
        err_encoding=args.err_encoding,
        sender=args.sender,
        failure_only=args.failure_only,
        mail_cmd=args.mail_cmd,
        nonempty=args.nonempty,
        no_stdout=args.no_stdout,
        no_stderr=args.no_stderr,
        split=args.split,
        to=args.to,
        utc=args.utc,
        mime_type=args.mime_type,
    )
    try:
        with DaemonContext(working_directory=args.chdir, umask=os.umask(0)):
            mailer.run(args.command, *args.args)
    except Exception as e:
        if isinstance(e, MailCmdError):
            e.update_email()
            with open(args.dead_letter, 'ab') as fp:
                fp.write(e.msg.compile())
        if args.logfile:
            # If no logfile was specified or this open() fails, die alone where
            # no one will ever know.
            sys.stderr = open(args.logfile, 'a')
                ### What encoding do I use for this???
            print(datetime.now().isoformat(), 'daemail', __version__,
                  'encountered an exception:', file=sys.stderr)
            traceback.print_exc()
            print('', file=sys.stderr)
            print('Configuration:', vars(mailer), file=sys.stderr)
            print('Chdir:', repr(args.chdir), file=sys.stderr)
            print('Command:', [args.command] + args.args, file=sys.stderr)
            if isinstance(e, MailCmdError):
                print('E-mail saved to',repr(args.dead_letter), file=sys.stderr)
            print('', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
