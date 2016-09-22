v0.4.0 (in development)
-----------------------
- Local timestamps will now include the local timezone offset if
  [`python-dateutil`](https://dateutil.readthedocs.io) is installed

- Added an `--mbox` option for "sending" e-mails to a local mbox file

- Gave `--chdir` a `-C` short form

- Added the `-i` option to the default `sendmail` command

- `--dead-letter` and `--logfile` (and `--mbox`) are now resolved relative to
  the directory in which daemail was started, not the directory specified with
  `--chdir`

- No more than one line ending sequence will be removed from
  `--smtp-password-file` (for the unlikely case in which the password ends with
  a newline)


v0.3.0 (2016-08-28)
-------------------
First usable release
