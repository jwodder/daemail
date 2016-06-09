[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active) [![MIT License](https://img.shields.io/github/license/jwodder/daemail.svg?maxAge=2592000)](https://opensource.org/licenses/MIT)

This is a Python script for running a command in the background and sending an
e-mail with its output once it's done.  It should work in both Python 2.7 and
Python 3.2+, the only external dependency being [the python-daemon
module](https://pypi.python.org/pypi/python-daemon).


Usage
=====

    daemail.py [--chdir <directory>]
               [-D|--dead-letter <file>]
               [-e|--encoding <encoding>]
               [-E|--err-encoding <encoding>]
               [-f|--from|--sender <address>]
               [-F|--failure-only]
               [-l|--logfile <logfile>]
               [-m|--mail-cmd <command>]
               [--mime <mime-type>]
               [-n|--nonempty]
               [--no-stdout]
               [--no-stderr]
               [--split]
               [-t|--to|--recipient|--rcpt <address>]
               [-Z|--utc]
               <command> [<arg> ...]

Options
-------

- `--chdir <directory>` — Change to `<directory>` before running `<command>`

- `-D <file>`, `--dead-letter <file>` — If an error occurs when trying to send,
  append the e-mail (including a description of the error) to `<file>`;
  defaults to `dead.letter` in the current directory or the directory specified
  with `--chdir`

- `-e <encoding>`, `--encoding <encoding>` — Expect the stdout (and stderr, if
  `--split` is not in effect) of `<command>` to be in the given encoding;
  defaults to the preferred encoding returned by Python's
  [`locale.getpreferredencoding`][preferred].  If decoding fails, the output
  will be attached to the e-mail as an `application/octet-stream` file.
    - When `--mime` is also given, this option has no effect other than to set
      the default value for `--err-encoding`.

- `-E <encoding>`, `--err-encoding <encoding>` — Expect the stderr of
  `<command>` to be in the given encoding; defaults to the value specified via
  `--encoding` or its default.  If decoding fails, the stderr output will be
  attached to the e-mail as an `application/octet-stream` file.
    - This option only has an effect when `--split` is given, either implicitly
      or explicitly.

- `-f <address>`, `--from <address>`, `--sender <address>` — Set the `From:`
  address of the e-mail; defaults to the current user at the local host

- `-F`, `--failure-only` — Only send an e-mail if the command exited with a
  nonzero status

- `-l <logfile>`, `--logfile <logfile>` — If something goes wrong after
  daemonization that prevents any e-mails from being sent, append a report to
  `<logfile>`

- `-m <command>`, `--mail-cmd <command>` — Send e-mail by passing the message
  to `<command>` (executed via the shell) on stdin; default command: `sendmail
  -t`

- `--mime <mime-type>` — Attach the standard output of `<command>` to the
  e-mail as an inline attachment with the given MIME type.  The MIME type may
  include parameters, e.g., `--mime "application/json; charset=utf-16"`.
  Implies `--split`.

- `-n`, `--nonempty` — Do not send an e-mail if the command exited successfully
  with no output

- `--no-stdout` — Don't capture the command's stdout; implies `--split`

- `--no-stderr` — Don't capture the command's stderr; implies `--split`

- `--split` — Capture the command's stdout and stderr separately rather than as
  a single stream

- `-t <address>`, `--to <address>`, `--recipient <address>`, `--rcpt <address>`
  — Set the recipient of the e-mail; defaults to the current user at the local
  host

- `-Z`, `--utc` — Show start & end times in UTC instead of local time

[preferred]: https://docs.python.org/3/library/locale.html#locale.getpreferredencoding
