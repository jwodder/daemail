#!/usr/bin/python
import argparse
from   datetime      import datetime
import email.charset
from   email.message import Message
import os
import re
import socket
import sys
import subprocess
from   daemon        import DaemonContext  # python-daemon

if sys.version_info[0] == 2:
    from pipes import quote
else:
    from shlex import quote

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
    # The command's output is all going to be in memory at some point anyway,
    # so why not start with `communicate`?
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
        "command": ' '.join(map(quote, cmd)),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='sender')
    parser.add_argument('-F', '--failed', action='store_true')
    parser.add_argument('-l', '--logfile', type=argparse.FileType('w+'))
    parser.add_argument('-m', '--mail-cmd', default='sendmail -t')
    parser.add_argument('-n', '--nonempty', action='store_true')
    parser.add_argument('-t', '--to')
    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.sender is None:
        args.sender = os.getlogin() + '@' + socket.gethostname()
    if args.to is None:
        args.to = os.getlogin() + '@' + socket.gethostname()
    with DaemonContext(stdout=args.logfile, stderr=args.logfile,
                       working_directory=os.getcwd()):
        proc = subcmd([args.command] + args.args, merged=True)
        if (proc["rc"] != 0 or not args.failed) and \
                (proc["stdout"] != '' or not args.nonempty):
            msg = Message()
            msg['Subject'] = ('[SUCCESS]' if proc["rc"] == 0 else '[FAILED]') \
                           + ' ' + proc["command"]
            msg['From'] = args.sender
            msg['To'] = args.to
            proc["stdout"] = re.sub(r'^', '> ', proc["stdout"], flags=re.M)
            body = 'Start Time:  {start}\n' \
                   'End Time:    {end}\n' \
                   'Exit Status: {rc}\n\n'.format(**proc)
            if proc["stdout"]:
                body += 'Output:\n' + proc["stdout"] + '\n'
            else:
                body += 'Output: none\n'
            chrset = email.charset.Charset('utf-8')
            chrset.body_encoding = email.charset.QP
            msg.set_payload(body, chrset)
            sendmail = subprocess.Popen(args.mail_cmd, shell=True,
                                        stdin=subprocess.PIPE)
            sendmail.communicate(str(msg))
            sys.exit(sendmail.returncode)
            ### TODO: Log an error if sendmail failed

if __name__ == '__main__':
    main()