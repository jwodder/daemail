v0.4.0 (in development)
-----------------------
- Local timestamps will now include the timezone offset

- Added an `--mbox` option for "sending" e-mails to a local mbox file

- Gave `--chdir` a `-C` short form

- Gave `--split` an `-S` short form

- Added the `-i` option to the default `sendmail` command

- `--dead-letter` and `--logfile` (and `--mbox`) are now resolved relative to
  the directory in which daemail was started, not the directory specified with
  `--chdir`

- No more than one line ending sequence will be removed from
  `--smtp-password-file` (for the unlikely case in which the password ends with
  a newline)

- Renamed `-m`/`--mail-cmd` to `-s`/`--sendmail`

- Added `--from-name` and `--to-name` options for setting the "real name" of
  the sender & recipient


v0.3.0 (2016-08-28)
-------------------
First usable release
