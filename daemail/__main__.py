from   codecs        import getdecoder
from   collections   import namedtuple
from   contextlib    import contextmanager
import locale
import netrc
import os
import sys
import traceback
import click
import daemon
from   daemon.daemon import DaemonError
from   .             import __version__
# Import runner instead of runner.CommandRunner etc. for mocking purposes
from   .             import reporter, runner, senders
from   .util         import AddressParamType, dt2stamp, dtnow, get_mime_type, \
                                multiline822, show_argv, split_content_type

DEFAULT_SENDMAIL = 'sendmail -i -t'

outfile_type = click.Path(writable=True, dir_okay=False, resolve_path=True)

def set_sender_cls(cls):
    def callback(ctx, param, value):
        if value is not None and value is not False:
            ctx.params['sender_cls'] = cls
            return value
    return callback

def use_smtp(ctx, param, value):
    if value is not None \
            and (ctx.params.get('sender_cls') is None
                or not issubclass(ctx.params['sender_cls'],senders.SMTPSender)):
        ctx.params['sender_cls'] = senders.SMTPSender
    return value

def pwd_getter(f):
    def callback(ctx, param, value):
        if value is not None and value is not False:
            ctx.params['smtp_password_getter'] = f(value)
    return callback

def plain_pwd(password):
    return lambda host, username: (username, password)

def password_file(fp):
    def get(host, username):
        with fp:
            smtp_password = fp.read()
        # Remove no more than one line ending sequence:
        if smtp_password.endswith('\n'):
            smtp_password = smtp_password[:-1]
        if smtp_password.endswith('\r'):
            # This should be unreachable due to Python opening files with
            # universal newlines enabled by default, but just in case...
            smtp_password = smtp_password[:-1]  # pragma: no cover
        return (username, smtp_password)
    return get

def netrc_getter(value):
    def get(host, username):
        nrc = netrc.netrc(None if value is True else value)
        login = nrc.authenticators(host)
        if login is not None:
            if username is not None:
                if login[0] in (None, '', username):
                    return (username, login[2])
            elif login[0] not in (None, ''):
                return (login[0], login[2])
        return (username, None)
    return get

def validate_encoding(ctx, param, value):
    if value is not None:
        try:
            getdecoder(value)
        except LookupError:
            raise click.BadParameter('{}: unknown encoding'.format(value))
    return value

def validate_mime_type(ctx, param, value):
    if value is not None:
        try:
            split_content_type(value)
        except ValueError:
            raise click.BadParameter('{}: invalid MIME type'.format(value))
    return value

def get_cwd():
    # Prefer $PWD to os.getcwd() as the former does not resolve symlinks
    return os.environ.get('PWD') or os.getcwd()


@click.command(name='daemail', context_settings={
    "allow_interspersed_args": False,
    "help_option_names": ["-h", "--help"],
})
@click.version_option(
    __version__,
    '-V', '--version',
    message = '%(prog)s %(version)s',
)
@click.option(
    '-C', '--chdir',
    metavar = 'DIR',
    default = get_cwd,
    help    = 'Change to this directory before running',
)
@click.option(
    '-D', '--dead-letter',
    metavar = 'MBOX',
    default = 'dead.letter',
    type    = outfile_type,
    help    = 'Append undeliverable mail to this file',
)
@click.option(
    '-e', '--encoding',
    callback = validate_encoding,
    help     = 'Encoding of stdout and stderr',
    metavar  = 'ENCODING',
)
@click.option(
    '-E', '--stderr-encoding',
    callback = validate_encoding,
    help     = 'Encoding of stderr',
    metavar  = 'ENCODING',
)
@click.option(
    '--foreground', '--fg',
    is_flag = True,
    help    = 'Run in the foreground instead of daemonizing',
)
@click.option(
    '-f', '--from-addr', '--from',
    type = AddressParamType(),
    help = 'From: address of e-mail',
)
@click.option(
    '-F', '--failure-only',
    is_flag = True,
    help    = 'Only send e-mail if command returned nonzero',
)
@click.option(
    '-l', '--logfile',
    default = 'daemail.log',
    type    = outfile_type,
    help    = 'Append unrecoverable errors to this file',
)
@click.option(
    '-M', '--mime-type', '--mime',
    callback = validate_mime_type,
    help     = 'Send output as attachment with given MIME type',
)
@click.option(
    '-n', '--nonempty',
    is_flag = True,
    help    = 'Only send e-mail if there was output or failure',
)
@click.option('--no-stdout', is_flag=True, help="Don't capture stdout")
@click.option('--no-stderr', is_flag=True, help="Don't capture stderr")
@click.option(
    '-S', '--split',
    is_flag = True,
    help    = 'Capture stdout and stderr separately',
)
@click.option(
    '--stdout-filename',
    metavar = 'FILENAME',
    help    = 'Send output as attachment with given filename',
)
@click.option(
    '-t', '--to-addr', '--to',
    metavar  = 'ADDRESS',
    type     = AddressParamType(),
    multiple = True,
    required = True,
    help     = 'To: address of e-mail',
)
@click.option('-Z', '--utc', is_flag=True, help='Use UTC timestamps')
@click.option(
    '-s', '--sendmail',
    metavar  = 'COMMAND',
    callback = set_sender_cls(senders.CommandSender),
    help     = 'Command for sending e-mail',
)
@click.option(
    '--mbox',
    help     = 'Append e-mail to this mbox file',
    type     = outfile_type,
    callback = set_sender_cls(senders.MboxSender),
)
@click.option(
    '--smtp-host',
    metavar  = 'HOST',
    callback = use_smtp,
    help     = 'SMTP server through which to send e-mail',
)
@click.option(
    '--smtp-port',
    type     = int,
    metavar  = 'PORT',
    callback = use_smtp,
    help     = 'Connect to --smtp-host on this port',
)
@click.option(
    '--smtp-username',
    metavar  = 'USERNAME',
    callback = use_smtp,
    help     = 'Username for authenticating with --smtp-host',
)
@click.option(
    '--smtp-password',
    metavar      = 'PASSWORD',
    callback     = pwd_getter(plain_pwd),
    expose_value = False,
    help         = 'Password for authenticating with --smtp-host',
)
@click.option(
    '--smtp-password-file',
    metavar      = 'FILE',
    type         = click.File(),
    callback     = pwd_getter(password_file),
    expose_value = False,
    help         = 'File containing password for --smtp-host',
)
@click.option(
    '--netrc',
    is_flag      = True,
    callback     = pwd_getter(netrc_getter),
    expose_value = False,
    help         ='Fetch SMTP password from ~/.netrc file',
)
@click.option(
    '--netrc-file',
    type         = click.Path(dir_okay=False),
    callback     = pwd_getter(netrc_getter),
    expose_value = False,
    help         = 'Fetch SMTP password from given netrc file',
)
# Implementing `--smtp-ssl` and `--smtp-starttls` as feature switches writing
# to `sender_cls` won't work, as click will overwrite `sender_cls` with `None`
# if neither option is given.
@click.option(
    '--smtp-ssl',
    is_flag      = True,
    callback     = set_sender_cls(senders.SMTP_SSLSender),
    expose_value = False,
    help         = 'Use SMTPS protocol',
)
@click.option(
    '--smtp-starttls',
    is_flag      = True,
    callback     = set_sender_cls(senders.StartTLSSender),
    expose_value = False,
    help         = 'Use SMTP protocol with STARTTLS',
)
@click.argument('command')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def main(
    command, args,
    chdir, foreground,
    logfile,
    from_addr, to_addr,
    failure_only, nonempty,
    no_stdout, no_stderr, split,
    encoding, stderr_encoding, mime_type, stdout_filename,
    utc,
    sendmail, mbox, dead_letter,
    smtp_host, smtp_port, smtp_username,
    sender_cls=None,
    smtp_password_getter=None,
):
    """ Daemonize a command and e-mail the results """

    if sender_cls is None:
        sender = senders.CommandSender(DEFAULT_SENDMAIL)
    elif sender_cls is senders.CommandSender:
        sender = sender_cls(sendmail)
    elif sender_cls is senders.MboxSender:
        sender = sender_cls(mbox)
    else:
        assert issubclass(sender_cls, senders.SMTPSender)
        if smtp_host is None:
            raise click.UsageError('--smtp-host is required for SMTP')
        password = None
        if smtp_password_getter is not None:
            smtp_username, password = \
                smtp_password_getter(smtp_host, smtp_username)
        if smtp_username is not None and password is None:
            password = click.prompt('SMTP password', hide_input=True, err=True)
        sender = sender_cls(smtp_host, smtp_port, smtp_username, password)

    if encoding is None:
        encoding = locale.getpreferredencoding(True)
    if stderr_encoding is None:
        stderr_encoding = encoding
    if stdout_filename is not None:
        if mime_type is None:
            mime_type = get_mime_type(stdout_filename)
        split = True
    elif mime_type is not None:
        stdout_filename = 'stdout'
        split = True

    daemail = Daemail(
        runner = runner.CommandRunner(
            no_stderr = no_stderr,
            no_stdout = no_stdout,
            split     = split,
        ),
        reporter = reporter.CommandReporter(
            encoding        = encoding,
            failure_only    = failure_only,
            from_addr       = from_addr,
            mime_type       = mime_type,
            nonempty        = nonempty,
            stderr_encoding = stderr_encoding,
            stdout_filename = stdout_filename,
            to_addrs        = to_addr,
            utc             = utc,
        ),
        mailer = senders.TryingSender(
            dead_letter_path = dead_letter,
            sender           = sender,
        ),
    )

    if foreground:
        ctx = chdir_context(chdir)
    else:
        ctx = daemon.DaemonContext(working_directory=chdir, umask=os.umask(0))
    try:
        with ctx:
            daemail.run(command, *args)
    except DaemonError:
        # Daemonization failed; report errors normally
        raise
    except Exception:
        # Daemonization succeeded but mailer failed; report errors to logfile.
        # If this open() fails, die alone where no one will ever know.
        with open(logfile, 'a') as fp:
            print('daemail:', __version__, file=fp)
            print('Command:', show_argv(command, *args), file=fp)
            print('Date:', dt2stamp(dtnow()), file=fp)
            print('Configuration:', file=fp)
            print(multiline822(daemail.shows_config()), file=fp)
            print('Chdir:', repr(chdir), file=fp)
            print('Traceback:', file=fp)
            print(multiline822(traceback.format_exc()), file=fp)
            print('', file=fp)
        sys.exit(1)


class Daemail(namedtuple('Daemail', 'runner reporter mailer')):
    # runner: CommandRunner
    # reporter: CommandReporter
    # mailer: TryingSender

    def run(self, command, *args):
        r = self.runner.run(command, *args)
        msg = self.reporter.report(r)
        if msg is not None:
            self.mailer.send(msg)

    def shows_config(self):
        s = ''
        s += '"From:" address: ' + str(self.reporter.from_addr) + '\n'
        s += '"To:" addresses:\n'
        for t in self.reporter.to_addrs:
            s += '  ' + str(t) + '\n'
        s += 'Outgoing mail:\n'
        for k,v in self.mailer.sender.about():
            s += '  {}: {}\n'.format(k,v)
        s += 'Dead letter mbox: ' + repr(self.mailer.dead_letter_path) + '\n'
        s += 'Split stdout/stderr: ' + yesno(self.runner.split) + '\n'
        s += 'Capture stdout: ' + yesno(not self.runner.no_stdout) + '\n'
        s += 'stdout encoding: ' + self.reporter.encoding + '\n'
        s += 'stdout MIME type: ' + str(self.reporter.mime_type) + '\n'
        s += 'stdout filename: ' + str(self.reporter.stdout_filename) + '\n'
        s += 'Capture stderr: ' + yesno(not self.runner.no_stderr) + '\n'
        s += 'stderr encoding: ' + self.reporter.stderr_encoding + '\n'
        s += 'Send iff failure: ' + yesno(self.reporter.failure_only) + '\n'
        s += 'Send iff nonempty: ' + yesno(self.reporter.nonempty) + '\n'
        s += 'UTC timestamps: ' + yesno(self.reporter.utc) + '\n'
        return s.rstrip('\n')


@contextmanager
def chdir_context(dirpath):
    old_cwd = get_cwd()
    os.chdir(dirpath)
    try:
        yield
    finally:
        ### TODO: Handle failure here:
        os.chdir(old_cwd)

def yesno(b):
    return 'yes' if b else 'no'

if __name__ == '__main__':
    main(prog_name=__package__)  # pragma: no cover
