- Redirect subcommand output to tempfiles instead of reading it all into
  memory?
    - Send large output as compressed attachments?
    - If compression fails (or if the compressed file exceeds a given limit on
      maximum attachment size), keep the file around and include its filepath
      in the e-mail
    - Add an option for redirecting output to a file (`/dev/null`?) but not
      sending it anyway, for those rare cases where the command behaves
      differently if its output is closed
- Invoke the sender in the directory from which daemail was started?
- Call `locale.getpreferredencoding(True)` once at the beginning of the program
  and then call it without arguments elsewhere?
- Make the internal API suitable for public exposure
- Improve the configuration settings dump in the logfile
    - Somehow bring back the sender configuration dump
- Use `time.monotonic` to calculate elapsed time
- Add a `--combine` option that is the negation of `--split` and rename
  `--split` to `--no-combine`?
- `show_argv`: Show, say, an `é` in an argument as `é`, assuming it decodes
  properly using the filesystem encoding (This could lead to problems with
  non-ASCII control/non-printable characters)

- Documentation:
    - Add docstrings
    - Include an example e-mail in the README
    - Add basic usage examples (using `--mime-type`/attachments, using
      `--encoding`, using `--smtp-host`, explanation of `--split`, etc.) to the
      README

- Write tests
    - `show_argv`:
        - Test non-printable characters without single-letter escapes?
        - Test non-simple arguments with equals signs
    - Do data-driven testing of e-mail composition?

New Features
------------
- If opening the logfile and/or dead letter file fails, write to syslog?
- Support format specifiers in the logfile and dead letter filenames
- Support reading stdin before daemonzing and passing the contents to the
  command?
- Support reading a shell script (or script for a given interpreter) from
  stdin?

- Options to add:
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
    - show command output when running in foreground?
    - don't include `stdout` on success/failure
    - Log dead letters to the logfile?
    - Log successes to the logfile?
    - Log info/debugging messages to the logfile?
    - Log e-mails not sent due to `--failure-only` or `--nonempty` to the
      logfile?
    - `--stdin <file>`?
    - `--stderr-filename`
    - `--stderr-mime-type`? (but when is stderr not plain text?)
    - Combine stdout and stderr in the same attachment?
    - Create a pidfile for the command and/or daemail?
    - `--forward`: while running the subcommand, forward any & all signals
      daemail receives to it
    - Send output to a given (non-temporary) file instead of adding it to the
      e-mail
    - `--cc`? `--bcc`?
    - only show the name of the command run in the subject line (i.e., omit the
      arguments)
    - Don't ASCIIfy the command for the subject line
    - command timeout?
    - Use the 'replace' error handler when decoding command stdout/stderr
    - `--shell` (for running a single argument via the shell)
