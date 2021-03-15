from   codecs        import getdecoder
from   email.headerregistry import Address
import locale
import os
from   pathlib       import Path
import sys
import traceback
from   typing        import Any, ContextManager, Optional, Tuple, Union
import attr
import click
import daemon
from   daemon.daemon import DaemonError
from   mailbits      import ContentType
from   morecontext   import dirchanged
from   outgoing      import from_config_file, get_default_configpath
from   .             import __version__
# Import runner instead of runner.CommandRunner etc. for mocking purposes
from   .             import reporter, runner, senders
from   .util         import AddressParamType, dt2stamp, dtnow, get_mime_type, \
                                multiline822, show_argv

outfile_type = click.Path(writable=True, dir_okay=False, resolve_path=True)

def validate_encoding(_ctx: click.Context, _param: click.Parameter, value: Any) -> Any:
    if value is not None:
        try:
            getdecoder(value)
        except LookupError:
            raise click.BadParameter(f'{value}: unknown encoding')
    return value

def validate_mime_type(_ctx: click.Context, _param: click.Parameter, value: Any) -> Any:
    if value is not None:
        try:
            ContentType.parse(value)
        except ValueError:
            raise click.BadParameter(f'{value}: invalid MIME type')
    return value

def get_cwd() -> str:
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
    "-c",
    "--config",
    type=click.Path(dir_okay=False),
    default=get_default_configpath,
    help="Specify the configuration file to use",
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
@click.argument('command')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def main(
    command: str,
    args: Tuple[str, ...],
    config: Union[Path, str],
    chdir: str,
    foreground: bool,
    logfile: str,
    from_addr: Optional[Address],
    to_addr: Tuple[Address],
    failure_only: bool,
    nonempty: bool,
    no_stdout: bool,
    no_stderr: bool,
    split: bool,
    encoding: Optional[str],
    stderr_encoding: Optional[str],
    mime_type: Optional[str],
    stdout_filename: Optional[str],
    utc: bool,
    dead_letter: str,
) -> None:
    """ Daemonize a command and e-mail the results """

    sender = from_config_file(config, fallback=False)

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

    ctx: ContextManager[Any]
    if foreground:
        ctx = dirchanged(chdir)
    else:
        ctx = daemon.DaemonContext(working_directory=chdir, umask=os.umask(0))
    try:
        with ctx:
            daemail.run(command, *args)
    except DaemonError:
        # Daemonization failed; report errors normally
        raise
    except Exception:
        if foreground:
            raise
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


@attr.s(auto_attribs=True)
class Daemail:
    runner: runner.CommandRunner
    reporter: reporter.CommandReporter
    mailer: senders.TryingSender

    def run(self, command: str, *args: str) -> None:
        r = self.runner.run(command, *args)
        msg = self.reporter.report(r)
        if msg is not None:
            self.mailer.send(msg)

    def shows_config(self) -> str:
        s = ''
        s += '"From:" address: ' + str(self.reporter.from_addr) + '\n'
        s += '"To:" addresses:\n'
        for t in self.reporter.to_addrs:
            s += '  ' + str(t) + '\n'
        s += f'Outgoing mail class: {type(self.mailer.sender)}\n'
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


def yesno(b: bool) -> str:
    return 'yes' if b else 'no'

if __name__ == '__main__':
    main(prog_name=__package__)  # pragma: no cover
