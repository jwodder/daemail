v0.6.0 (in development)
-----------------------
- **Breaking**: Removed `--to-name` and `--from-name` (deprecated in v0.5.0)

- Dropped support for Python versions earlier than 3.4

- Internal rewrites to use Python 3's new `email` API

- Added a `--foreground` option for disabling daemonization


v0.5.0 (2017-02-05)
-------------------
- If an error occurs during daemonization (e.g., because the `--chdir` argument
  is not a directory), a normal error traceback will be printed to stderr
  instead of writing a report to the logfile.

- `--to-addr` can now be specified on the command line multiple times in order
  to send to multiple addresses

- Arguments to `--to-addr` and `--from-addr` can now be in the form "`Real Name
  <address@example.com>`".  `--to-name` and `--from-name` are now deprecated
  and will be removed in a future version.


v0.4.0 (2016-11-05)
-------------------
- **Breaking**: `--dead-letter` and `--logfile` (and `--mbox`) are now resolved
  relative to the directory in which daemail was started, not the directory
  specified with `--chdir`

- **Breaking**: No more than one line ending sequence will be removed from
  `--smtp-password-file` (for the unlikely case in which the password ends with
  a newline)

- **Breaking**: Renamed `-m`/`--mail-cmd` to `-s`/`--sendmail`

- **Breaking**: Renamed `--err-encoding` to `--stderr-encoding` (The `-E` short
  option remains unchanged)

- Local timestamps now include the timezone offset

- Added an `--mbox` option for "sending" e-mails to a local mbox file

- Gave `--chdir` a `-C` short form

- Gave `--split` an `-S` short form

- Added the `-i` option to the default `sendmail` command

- Added `--from-name` and `--to-name` options for setting the "real name" of
  the sender & recipient

- Added a `--stdout-filename` option for specifying the name (and default MIME
  type) of the stdout attachment

- Added `--netrc` and `--netrc-file` options for reading the SMTP username &
  password from a netrc file

- Improvements to error message formatting


v0.3.0 (2016-08-28)
-------------------
First usable release
