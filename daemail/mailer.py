from   collections import namedtuple
import locale
import subprocess
import traceback
from   .message    import DraftMessage
from   .senders    import MboxSender
from   .util       import MailCmdError, mail_quote, nowstamp, rc_with_signal, \
                            show_argv

class CommandMailer(namedtuple('CommandMailer', '''
    sender dead_letter to_addrs from_addr failure_only nonempty no_stdout
    no_stderr split encoding stderr_encoding utc mime_type stdout_filename
''')):
    def run(self, command, *args):
        try:
            results = self.subcmd(command, *args)
        except Exception:
            msg = self.err2mail(command, args)
        else:
            if results["rc"] == 0 and (self.failure_only or
                    self.nonempty and not (results["stdout"] or
                                           results["stderr"])):
                return
            msg = self.cmd2mail(results, command, args)
        self.send(msg)

    def subcmd(self, command, *args):
        params = {}
        if self.split or self.no_stdout or self.no_stderr:
            params = {
                "stdout": None if self.no_stdout else subprocess.PIPE,
                "stderr": None if self.no_stderr else subprocess.PIPE,
            }
        else:
            params = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        start = nowstamp(self.utc)
        p = subprocess.Popen((command,) + args, **params)
        # The command's output is all going to be in memory at some point
        # anyway, so why not start with `communicate`?
        out, err = p.communicate()
        end = nowstamp(self.utc)
        return {
            "rc": p.returncode,
            "start": start,
            "end": end,
            "stdout": out,
            "stderr": err,
            #"pid": p.pid,
        }

    def cmd2mail(self, results, command, args):
        msg = DraftMessage(
            from_addr = self.from_addr,
            to_addrs  = self.to_addrs,
            subject   = '[{}] {}'.format(
                'DONE' if results["rc"] == 0 else 'FAILED',
                show_argv(command, *args),
            ),
        )
        results["rc"] = rc_with_signal(results["rc"])
        msg.addtext('Start Time:  {start}\n'
                    'End Time:    {end}\n'
                    'Exit Status: {rc}\n'.format(**results))
        # An empty byte string is always an empty character string and vice
        # versa, right?
        if results["stdout"]:
            msg.addtext('\nOutput:\n')
            if self.mime_type is not None:
                msg.addmimeblob(results["stdout"], self.mime_type,
                                self.stdout_filename)
            else:
                msg.addblobquote(results["stdout"], self.encoding, 'stdout')
        elif results["stdout"] is not None:
            msg.addtext('\nOutput: none\n')
        if results["stderr"]:
            # If stderr was captured separately but is still empty, don't
            # bother saying "Error Output: none".
            msg.addtext('\nError Output:\n')
            msg.addblobquote(results["stderr"], self.stderr_encoding, 'stderr')
        return msg

    def err2mail(self, command, args):
        msg = DraftMessage(
            from_addr = self.from_addr,
            to_addrs  = self.to_addrs,
            subject   = '[ERROR] ' + show_argv(command, *args),
        )
        msg.addtext('An error occurred while attempting to run the command:\n'
                    + mail_quote(traceback.format_exc()))
        return msg

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
            MboxSender(self.dead_letter).send(msg.compile())
