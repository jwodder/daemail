v0.7.0 (2021-03-15)
-------------------
- Drop support for Python 3.5
- Support Python 3.9
- **Breaking**: All of the sending options have been removed from the
  command-line interface.  Sending is now performed via the
  [`outgoing`](https://github.com/jwodder/outgoing) library, which is
  configured via a configuration file.
- Errors that occur when daemonization is disabled will now be reported
  directly to the screen instead of to the logfile

v0.6.0 (2020-03-17)
-------------------
- Massive internal rewrites
- Dropped support for Python versions earlier than 3.5
- Support Python 3.6 through 3.8
- Added a `--foreground` option for disabling daemonization
- **Breaking**: Removed `--to-name` and `--from-name` (deprecated in v0.5.0)
- **Breaking**: `--dead-letter`, `--logfile`, and `--mbox` now resolve symbolic
  links before daemonization
- If no `--chdir` argument is supplied, change directory to the value of
  `$PWD`, falling back to the old value of `getcwd()` only if the environment
  variable isn't set
- `--encoding`, `--stderr-encoding`, and `--mime-type` arguments are now
  validated before daemonization
- Deduction of the MIME type from `--stdout-filename`'s extension now better
  handles names of compressed files

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
