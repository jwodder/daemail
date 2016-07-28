from   __future__ import unicode_literals
from   datetime   import datetime
import locale
import os
import subprocess
import sys
import traceback
from   .          import USER_AGENT
from   .message   import DraftMessage
from   .util      import mail_quote, rc_with_signal

if sys.version_info[0] == 2:
    from pipes import quote
else:
    from shlex import quote

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
