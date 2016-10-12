- Look into minimum version requirements for `python-daemon`
- When an attempt to send over SMTP fails, should the SMTP host & username be
  recorded in the dead letter?
- Redirect subcommand output to tempfiles instead of reading it all into
  memory?
- What happens if the `chdir` fails while daemonizing?  Should that be handled
  somehow?
- Should `--to-addr` not be required when sending to an mbox?
- Execute `--sendmail` in the directory in which daemail was started?
- Look into handling of encoding issues with SMTP passwords
- Check handling of non-ASCII e-mail addresses
- Try to drastically simplify CommandMailer's constructor
- Drop support for Python 2?

- Documentation:
    - Add docstrings
    - Include an example e-mail in the README
    - Add basic usage examples (using `--mime-type`/attachments, using
      `--encoding`, using `--smtp-host`, explanation of `--split`, etc.) to the
      README

- Logging:
    - Make logfile entries look like mbox entries?
    - Improve (or eliminate?) the configuration settings dump in the logfile
    - Write error messages to stderr instead of the logfile if daemonization
      fails

- Try to write tests
    - Set up Travis integration
    - Ensure this works in both Python 2 and Python 3
        - Test handling of non-ASCII characters in `--smtp-password-file` in
          both Python 2 and Python 3
    - Use a mock Sender class
    - Combinations of possibilities to test:
        - command succeeds/fails/errors/is killed by a signal
        - command output can/can't be decoded/is empty
        - mail command succeeds/fails/errors/is killed by a signal
        - mail command output can/can't be decoded/is empty
    - Test handling of attachments containing "From " at the beginning of a
      line (especially when writing to dead.letter) or a line with just a
      period (Can either of these happen?)
    - `show_argv`:
        - Test non-printable characters without single-letter escapes?
        - Test non-simple arguments with equals signs
    - Do data-driven testing of e-mail composition

New Features
------------
- If opening the logfile and/or dead letter file fails, write to syslog?
- Support pre-specifying all options via an INI-style config file
  (`~/.config/daemail.cfg`)
    - This will require implementing `--no-split`, `--no-utc`, etc. options for
      overriding config file options on the command line
- Support format specifiers in the logfile and dead letter filenames
- Allow specifying multiple `--to`s (and `--cc`s and `--bcc`s?) on the command
  line
- `show_argv`: Show, say, an `é` in an argument as `é`, assuming it decodes
  properly using the filesystem encoding (This could lead to problems with
  non-ASCII control/non-printable characters)
- When running the subcommand, should daemail forward any & all signals
  received to it?
- Support format specifiers in `--sendmail` for interpolating the To & From
  addresses (and subject?)
- Should the `dead_letter` parameter of `CommandMailer` be a sender object
  instead of filepath?
- Support for Gmail's OAuth?  (Save for a much later version)
- Support reading stdin before daemonzing and passing the contents to the
  command?
- Support reading the SMTP username & password from `~/.netrc`?
- Use the `encoding` value returned by `mimetypes.guess_type`?

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
    - `--no-daemonize` (for debugging)
        - Also add an option for teeing the output?
    - include environment variables in e-mail?
    - don't include `stdout` on success/failure
    - Log dead letters to the logfile?
    - Log successes to the logfile?
    - Log info/debugging messages to the logfile?
    - Log e-mails not sent due to `--failure-only` or `--nonempty` to the
      logfile?
    - (try to) e-mail fatal errors instead of writing them to the logfile?
    - `--stdin <file>`?
    - certificates to use with SSL over SMTP
    - `--stderr-filename`
    - `--stderr-mime-type`? (but when is stderr not plain text?)
    - Combine stdout and stderr in the same attachment?
