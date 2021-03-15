import locale
from   subprocess import CalledProcessError
import traceback
import attr
from   eletter    import reply_quote
from   outgoing   import Sender, from_dict
from   .message   import DraftMessage
from   .util      import rc_with_signal

@attr.s(auto_attribs=True)
class TryingSender:
    """
    Tries to send a message via the given sender object, falling back to
    sending to the mbox at ``dead_letter_path`` if that fails
    """

    sender: Sender
    dead_letter_path: str

    def send(self, msg: DraftMessage) -> None:
        msgobj = msg.compile()
        try:
            self.sender.send(msgobj)
        except Exception as e:
            msg.addtext(
                '\nAdditionally, an error occurred while trying to send'
                ' this e-mail:\n\n'
            )
            if isinstance(e, CalledProcessError):
                msg.addtext(f'Command: {e.cmd}\n')
                msg.addtext(f'Exit Status: {rc_with_signal(e.returncode)}\n')
                if e.output:
                    msg.addtext('\nOutput:\n')
                    msg.addblobquote(
                        e.output,
                        locale.getpreferredencoding(True),
                        'sendmail-output',
                   )
                else:
                    msg.addtext('\nOutput: none\n')
                if e.stderr:
                    msg.addtext('\nStderr:\n')
                    msg.addblobquote(
                        e.stderr,
                        locale.getpreferredencoding(True),
                        'sendmail-stderr',
                   )
            else:
                msg.addtext(reply_quote(traceback.format_exc()))
            ### TODO: Handle failures here!
            with from_dict({"method": "mbox", "path": self.dead_letter_path}) \
                    as sender:
                sender.send(msg.compile())
