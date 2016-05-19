This is a Python script for running a command in the background and sending an
e-mail once it's done.  It should work in both Python 2.7 and Python 3.2+, the
only external dependency being [the python-daemon
module](https://pypi.python.org/pypi/python-daemon).


Usage
=====

    daemail.py [-D|--dead-letter <file>]
               [-e|--encoding <encoding>]
               [-E|--err-encoding <encoding>]
               [-f|--from|--sender <address>]
               [-F|--failed]
               [-l|--logfile <logfile>]
               [-m|--mail-cmd <command>]
               [-n|--nonempty]
               [--no-stdout]
               [--no-stderr]
               [--split]
               [-t|--to|--recipient|--rcpt <address>]
               <command> [<arg> ...]

Options
-------

- `-D <file>`, `--dead-letter <file>` — If an error occurs when trying to send,
  append the e-mail (including a description of the error) to `<file>`;
  defaults to `dead.letter` in the current directory

- `-e <encoding>`, `--encoding <encoding>` — Expect the stdout (and stderr,
  unless overridden by `--err-encoding`) of `<command>` to be in the given
  encoding; defaults to the preferred encoding returned by Python's
  [`locale.getpreferredencoding`][preferred]

- `-E <encoding>`, `--err-encoding <encoding>` — Expect the stderr of
  `<command>` to be in the given encoding; defaults to the value specified via
  `--encoding` or its default

- `-f <address>`, `--from <address>`, `--sender <address>` — Set the `From:`
  address of the e-mail; defaults to the current user at the local host

- `-F`, `--failed` — Only send an e-mail if the command exits with a nonzero
  status

- `-l <logfile>`, `--logfile <logfile>` — If something goes wrong after
  daemonization that prevents any e-mails from being sent, append a report to
  `<logfile>`

- `-m <command>`, `--mail-cmd <command>` — Send e-mail by passing the message
  to `<command>` (executed via the shell) on stdin; default command: `sendmail
  -t`

- `-n`, `--nonempty` — Only send an e-mail if the command emitted any output

- `--no-stdout` — Don't capture the command's stdout; implies `--split`

- `--no-stderr` — Don't capture the command's stderr; implies `--split`

- `--split` — Capture the command's stdout and stderr separately rather than as
  a single stream

- `-t <address>`, `--to <address>`, `--recipient <address>`, `--rcpt <address>`
  — Set the recipient of the e-mail; defaults to the current user at the local
  host


[preferred]: https://docs.python.org/3/library/locale.html#locale.getpreferredencoding
