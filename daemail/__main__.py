from   __future__    import print_function, unicode_literals
import argparse
from   getpass       import getpass
import netrc
import os
import os.path
import sys
import traceback
from   daemon        import DaemonContext  # python-daemon
from   daemon.daemon import DaemonError
from   .             import __version__
from   .             import senders
from   .mailer       import CommandMailer
from   .util         import addr_arg, multiline822, nowstamp, show_argv

def main():
    pwd = os.getcwd()
    parser = argparse.ArgumentParser(
        prog='daemail',
        description='Daemonize a command and e-mail the results',
    )
    parser.add_argument('-C', '--chdir', metavar='DIR', default=pwd,
                        help="Change to this directory before running")
    parser.add_argument('-D', '--dead-letter', metavar='MBOX',
                        default='dead.letter',
                        help="Append undeliverable mail to this file")
    parser.add_argument('-e', '--encoding',
                        help='Encoding of stdout and stderr')
    parser.add_argument('-E', '--stderr-encoding', help='Encoding of stderr',
                        metavar='ENCODING')
    parser.add_argument('-f', '--from-addr', '--from', type=addr_arg,
                        help='From: address of e-mail')
    parser.add_argument('--from-name', help='name to use in From: address')
    parser.add_argument('-F', '--failure-only', action='store_true',
                        help='Only send e-mail if command returned nonzero')
    parser.add_argument('-l', '--logfile', default='daemail.log',
                        help='Append unrecoverable errors to this file')
    parser.add_argument('-M', '--mime-type', '--mime',
                        help='Send output as attachment with given MIME type')
    parser.add_argument('-n', '--nonempty', action='store_true',
                        help='Only send e-mail if there was output or failure')
    parser.add_argument('--no-stdout', action='store_true',
                        help="Don't capture stdout")
    parser.add_argument('--no-stderr', action='store_true',
                        help="Don't capture stderr")
    parser.add_argument('-S', '--split', action='store_true',
                        help='Capture stdout and stderr separately')
    parser.add_argument('--stdout-filename', metavar='FILENAME',
                        help='Send output as attachment with given filename')
    parser.add_argument('-t', '--to-addr', '--to', metavar='RECIPIENT',
                        type=addr_arg, action='append', required=True,
                        help='To: address of e-mail')
    parser.add_argument('--to-name', help='name to use in To: address')
    parser.add_argument('-V', '--version', action='version',
                                           version='daemail ' + __version__)
    parser.add_argument('-Z', '--utc', action='store_true',
                        help='Use UTC timestamps')

    sendarg = parser.add_mutually_exclusive_group()
    sendarg.add_argument('-s', '--sendmail', metavar='COMMAND',
                         default='sendmail -i -t',
                         help='Command for sending e-mail')
    sendarg.add_argument('--mbox', help='Append e-mail to this mbox file')
    sendarg.add_argument('--smtp-host', metavar='HOST',
                        help='SMTP server through which to send e-mail')

    parser.add_argument('--smtp-port', type=int, metavar='PORT',
                        help='Connect to --smtp-host on this port')
    parser.add_argument('--smtp-username', metavar='USERNAME',
                        help='Username for authenticating with --smtp-host')

    smtp_pass = parser.add_mutually_exclusive_group()
    smtp_pass.add_argument('--smtp-password', metavar='PASSWORD',
                           help='Password for authenticating with --smtp-host')
    smtp_pass.add_argument('--smtp-password-file', metavar='FILE',
                           type=argparse.FileType('r'),
                           help='File containing password for authenticating'
                                ' with --smtp-host')
    smtp_pass.add_argument('--netrc', action='store_true',
                           help='Fetch SMTP password from ~/.netrc file')
    smtp_pass.add_argument('--netrc-file',
                           help='Fetch SMTP password from given netrc file')

    smtp_ssl = parser.add_mutually_exclusive_group()
    smtp_ssl.add_argument('--smtp-ssl', action='store_true',
                          help='Use SMTPS protocol')
    smtp_ssl.add_argument('--smtp-starttls', action='store_true',
                          help='Use SMTP protocol with STARTTLS')

    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.smtp_host is not None:
        if args.smtp_ssl:
            cls = senders.SMTP_SSLSender
        elif args.smtp_starttls:
            cls = senders.StartTLSSender
        else:
            cls = senders.SMTPSender
        username = args.smtp_username
        password = args.smtp_password
        if args.smtp_password_file is not None:
            assert password is None
            with args.smtp_password_file as fp:
                password = fp.read()
            # Remove no more than one line ending sequence:
            if password.endswith('\n'):
                password = password[:-1]
            if password.endswith('\r'):
                password = password[:-1]
        elif args.netrc or args.netrc_file is not None:
            assert password is None
            nrc = netrc.netrc(None if args.netrc else args.netrc_file)
            login = nrc.authenticators(args.smtp_host)
            if login is not None:
                if username is not None:
                    if login[0] is None or login[0] == username:
                        password = login[2]
                elif login[0] is not None:
                    username = login[0]
                    password = login[2]
        if username is not None and password is None:
            password = getpass('SMTP password: ')
        sender = cls(args.smtp_host, args.smtp_port, username, password)
    elif any(a.startswith(('smtp_', 'netrc')) and
                getattr(args, a) not in (None, False)
             for a in vars(args)):
        sys.exit('daemail: --smtp-* options cannot be specified without'
                 ' --smtp-host')
    elif args.mbox is not None:
        sender = senders.MboxSender(os.path.join(pwd, args.mbox))
    else:
        sender = senders.CommandSender(args.sendmail)

    if args.from_name is not None and args.from_addr is not None:
        if args.from_addr[0] == '':
            args.from_addr = (args.from_name, args.from_addr[1])
        else:
            sys.exit('daemail: --from-name cannot be used when --from-addr'
                     ' includes a realname')

    if args.to_name is not None:
        if len(args.to_addr) == 1 and args.to_addr[0][0] == '':
            args.to_addr[0] = (args.to_name, args.to_addr[0][1])
        else:
            sys.exit('daemail: --to-name can only be used with a single'
                     ' --to-addr without a realname')

    mailer = CommandMailer(
        encoding=args.encoding,
        stderr_encoding=args.stderr_encoding,
        from_addr=args.from_addr,
        failure_only=args.failure_only,
        sender=sender,
        nonempty=args.nonempty,
        no_stdout=args.no_stdout,
        no_stderr=args.no_stderr,
        split=args.split,
        to_addrs=args.to_addr,
        utc=args.utc,
        mime_type=args.mime_type,
        stdout_filename=args.stdout_filename,
        dead_letter=os.path.join(pwd, args.dead_letter),
    )

    try:
        with DaemonContext(working_directory=args.chdir, umask=os.umask(0)):
            mailer.run(args.command, *args.args)
    except DaemonError:
        # Daemonization failed; report errors normally
        raise
    except Exception:
        # Daemonization succeeded but mailer failed; report errors to logfile
        # If this open() fails, die alone where no one will ever know.
        sys.stderr = open(os.path.join(pwd, args.logfile), 'a')
            # This will be a bytes stream in Python 2 (with Unicode strings
            # implicitly encoded upon printing) and a text stream in Python 3.
        print('daemail:', __version__, file=sys.stderr)
        print('Command:', show_argv(args.command, *args.args), file=sys.stderr)
        print('Date:', nowstamp(), file=sys.stderr)
        print('Configuration:', vars(mailer), file=sys.stderr)
        print('Chdir:', repr(args.chdir), file=sys.stderr)
        print('Traceback:', file=sys.stderr)
        print(multiline822(traceback.format_exc()), file=sys.stderr)
        print('', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
