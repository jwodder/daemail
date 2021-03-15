from   email.headerregistry import Address
from   typing               import List, Optional, Union
import attr
from   eletter              import reply_quote
# Access `show_argv()` through `util` for mocking purposes
from   .                    import util
from   .message             import DraftMessage
from   .runner              import CommandError, CommandResult
from   .util                import address_list, dt2stamp, rc_with_signal

@attr.s(auto_attribs=True)
class CommandReporter:
    encoding: str
    failure_only: bool
    from_addr: Optional[Address]
    mime_type: Optional[str]
    nonempty: bool
    stderr_encoding: str
    stdout_filename: Optional[str]  # non-None iff mime_type is non-None
    to_addrs: List[Address] = attr.ib(converter=address_list)
    utc: bool

    def report(self, result: Union[CommandResult, CommandError]) \
            -> Optional[DraftMessage]:
        if isinstance(result, CommandError):
            msg = DraftMessage(
                from_addr = self.from_addr,
                to_addrs  = self.to_addrs,
                subject   = '[ERROR] ' + util.show_argv(*result.argv),
            )
            msg.addtext(
                'An error occurred while attempting to run the command:\n'
                + reply_quote(result.tb)
            )
            return msg
        else:
            if result.rc == 0 and (self.failure_only
                    or self.nonempty and not (result.stdout or result.stderr)):
                return None
            msg = DraftMessage(
                from_addr = self.from_addr,
                to_addrs  = self.to_addrs,
                subject   = '[{}] {}'.format(
                    'DONE' if result.rc == 0 else 'FAILED',
                    util.show_argv(*result.argv),
                ),
            )
            msg.addtext(
                f'Start Time:  {dt2stamp(result.start, self.utc)}\n'
                f'End Time:    {dt2stamp(result.end, self.utc)}\n'
                f'Exit Status: {rc_with_signal(result.rc)}\n'
            )
            # An empty byte string is always an empty character string and vice
            # versa, right?
            if result.stdout:
                msg.addtext('\nOutput:\n')
                if self.mime_type is not None:
                    assert self.stdout_filename is not None
                    msg.addmimeblob(result.stdout, self.mime_type,
                                    self.stdout_filename)
                else:
                    msg.addblobquote(result.stdout, self.encoding, 'stdout')
            elif result.stdout is not None:
                msg.addtext('\nOutput: none\n')
            if result.stderr:
                # If stderr was captured separately but is still empty, don't
                # bother saying "Error Output: none".
                msg.addtext('\nError Output:\n')
                msg.addblobquote(result.stderr, self.stderr_encoding, 'stderr')
            return msg
