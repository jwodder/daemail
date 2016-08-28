from   __future__ import print_function, unicode_literals
import argparse
from   datetime   import datetime
from   getpass    import getpass
import os
import sys
import traceback
from   daemon     import DaemonContext  # python-daemon
from   .          import __version__
from   .          import senders
from   .mailer    import CommandMailer

def main():
    parser = argparse.ArgumentParser(
        prog='daemail',
        description='Daemonize a command and e-mail the results',
    )
    parser.add_argument('--chdir', metavar='DIR', default=os.getcwd(),
                        help="Change to this directory before running")
    parser.add_argument('-D', '--dead-letter', metavar='MBOX',
                        help="Append undeliverable mail to this file")
    parser.add_argument('-e', '--encoding',
                        help='Set encoding of stdout and stderr')
    parser.add_argument('-E', '--err-encoding', help='Set encoding of stderr',
                        metavar='ENCODING')
    parser.add_argument('-f', '--from-addr', '--from',
                        help='From: address of e-mail')
    parser.add_argument('-F', '--failure-only', action='store_true',
                        help='Only send e-mail if command returned nonzero')
    parser.add_argument('-l', '--logfile', default='daemail.log',
                        help='Append unrecoverable errors to this file')
    parser.add_argument('-m', '--mail-cmd', metavar='COMMAND',
                        help='Command for sending e-mail')
    parser.add_argument('-M', '--mime-type', '--mime',
                        help='Send output as attachment with given MIME type')
    parser.add_argument('-n', '--nonempty', action='store_true',
                        help='Only send e-mail if there was output or failure')
    parser.add_argument('--no-stdout', action='store_true',
                        help="Don't capture stdout")
    parser.add_argument('--no-stderr', action='store_true',
                        help="Don't capture stderr")
    parser.add_argument('--smtp-host', metavar='HOST',
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
    smtp_ssl = parser.add_mutually_exclusive_group()
    smtp_ssl.add_argument('--smtp-ssl', action='store_true',
                          help='Use SMTPS protocol')
    smtp_ssl.add_argument('--smtp-starttls', action='store_true',
                          help='Use SMTP protocol with STARTTLS')
    parser.add_argument('--split', action='store_true',
                        help='Capture stdout and stderr separately')
    parser.add_argument('-t', '--to-addr', '--to', metavar='RECIPIENT',
                        help='To: address of e-mail', required=True)
    parser.add_argument('-V', '--version', action='version',
                                           version='daemail ' + __version__)
    parser.add_argument('-Z', '--utc', action='store_true',
                        help='Use UTC timestamps')
    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.smtp_host is not None:
        if args.mail_cmd is not None:
            raise SystemExit('daemail: --mail-cmd and --smtp-host are mutually'
                             ' exclusive')
        if args.smtp_ssl:
            cls = senders.SMTP_SSLSender
        elif args.smtp_starttls:
            cls = senders.StartTLSSender
        else:
            cls = senders.SMTPSender
        if args.smtp_password_file is not None:
            with args.smtp_password_file as fp:
                args.smtp_password = fp.read().rstrip('\r\n')
        if args.smtp_username is not None and args.smtp_password is None:
            args.smtp_password = getpass('SMTP password: ')
        sender = cls(args.smtp_host, args.smtp_port, args.smtp_username,
                     args.smtp_password)
    elif any(a.startswith('smtp_') and getattr(args, a) not in (None, False)
             for a in vars(args)):
        raise SystemExit('daemail: --smtp-* options cannot be specified without'
                         ' --smtp-host')
    else:
        sender = senders.CommandSender(args.mail_cmd)

    mailer = CommandMailer(
        encoding=args.encoding,
        err_encoding=args.err_encoding,
        from_addr=args.from_addr,
        failure_only=args.failure_only,
        sender=sender,
        nonempty=args.nonempty,
        no_stdout=args.no_stdout,
        no_stderr=args.no_stderr,
        split=args.split,
        to_addr=args.to_addr,
        utc=args.utc,
        mime_type=args.mime_type,
        dead_letter=args.dead_letter,
    )

    try:
        with DaemonContext(working_directory=args.chdir, umask=os.umask(0)):
            mailer.run(args.command, *args.args)
    except Exception:
        # If this open() fails, die alone where no one will ever know.
        sys.stderr = open(args.logfile, 'a')
            ### TODO: What encoding do I use for this???
        print(datetime.now().isoformat(), 'daemail', __version__,
              'encountered an exception:', file=sys.stderr)
        traceback.print_exc()
        print('', file=sys.stderr)
        print('Configuration:', vars(mailer), file=sys.stderr)
        print('Chdir:', repr(args.chdir), file=sys.stderr)
        print('Command:', [args.command] + args.args, file=sys.stderr)
        print('', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
