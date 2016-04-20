#!/usr/bin/python
import argparse
import codecs
from   datetime      import datetime
import email.charset
from   email.message import Message
import os
import socket
import sys
import subprocess
from   daemon        import DaemonContext  # python-daemon

def subcmd(cmd, merged=False, stdout=False, stderr=False):
    params = {}
    if merged:
        params = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
    else:
        if stdout:
            params["stdout"] = subprocess.PIPE
        if stderr:
            params["stderr"] = subprocess.PIPE
    start = datetime.now()
    p = subprocess.Popen(cmd, **params)
    out, err = p.communicate()
    end = datetime.now()
    return {
        "rc": p.returncode,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "stdout": out,
        "stderr": err,
        "pid": p.pid,
        "argv0": cmd[0],
        "command": ' '.join(cmd),  ### TODO: Quote arguments
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='sender')
    parser.add_argument('-t', '--to')
    parser.add_argument('-s', '--subject', default='Finished: {command}')
    parser.add_argument('-F', '--failure-only', action='store_true')
    parser.add_argument('-m', '--mail-cmd', default='sendmail -t')
    parser.add_argument('-l', '--logfile', type=argparse.FileType('w+'))
    parser.add_argument('-b', '--body', default='''\
Started: {start}
Finished: {end}
Return code: {rc}

{stdout}
''')
    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.sender is None:
        args.sender = os.getlogin() + '@' + socket.gethostname()
    if args.to is None:
        args.to = os.getlogin() + '@' + socket.gethostname()
    with DaemonContext(stdout=args.logfile, stderr=args.logfile, working_directory=os.getcwd()):
        proc = subcmd([args.command] + args.args, merged=True)
        if proc["rc"] != 0 or not args.failure_only:
            msg = Message()
            msg['Subject'] = args.subject.format(**proc)
            msg['From'] = args.sender
            msg['To'] = args.to
            body = codecs.decode(args.body, 'string_escape').format(**proc)
            ### Use 'unicode_escape' instead?
            chrset = email.charset.Charset('utf-8')
            chrset.body_encoding = email.charset.QP
            msg.set_payload(body, chrset)
            sendmail = subprocess.Popen(args.mail_cmd, shell=True,
                                        stdin=subprocess.PIPE)
            sendmail.communicate(str(msg))
            sys.exit(sendmail.returncode)


if __name__ == '__main__':
    main()
