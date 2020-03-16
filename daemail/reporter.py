from   collections import namedtuple
# Access `show_argv()` through `util` for mocking purposes
from   .           import util
from   .message    import DraftMessage
from   .util       import dt2stamp, mail_quote, rc_with_signal

class CommandReporter(namedtuple('CommandReporter', '''
    encoding failure_only from_addr mime_type nonempty stderr_encoding
    stdout_filename to_addrs utc
''')):
    # encoding: str
    # failure_only: bool
    # from_addr: email.headerregistry.Address
    # mime_type: Optional[str]
    # nonempty: bool
    # stderr_encoding: str
    # stdout_filename: Optional[str]  # non-None iff mime_type is non-None
    # to_addrs: list[email.headerregistry.Address]
    # utc: bool

    def report(self, result):
        if result.errored:
            msg = DraftMessage(
                from_addr = self.from_addr,
                to_addrs  = self.to_addrs,
                subject   = '[ERROR] ' + util.show_argv(*result.argv),
            )
            msg.addtext(
                'An error occurred while attempting to run the command:\n'
                + mail_quote(result.format_traceback())
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
                'Start Time:  {}\n'
                'End Time:    {}\n'
                'Exit Status: {}\n'.format(
                    dt2stamp(result.start, self.utc),
                    dt2stamp(result.end, self.utc),
                    rc_with_signal(result.rc),
                )
            )
            # An empty byte string is always an empty character string and vice
            # versa, right?
            if result.stdout:
                msg.addtext('\nOutput:\n')
                if self.mime_type is not None:
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
