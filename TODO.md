- Redirect subcommand output to tempfiles instead of reading it all into
  memory?
    - Send large output as compressed attachments?
    - If compression fails (or if the compressed file exceeds a given limit on
      maximum attachment size), keep the file around and include its filepath
      in the e-mail
    - Add an option for redirecting output to a file (`/dev/null`?) but not
      sending it anyway, for those rare cases where the command behaves
      differently if its output is closed
- Should `--to-addr` not be required when sending to an mbox?
- Execute `--sendmail` in the directory in which daemail was started?
- Look into handling of encoding issues with SMTP passwords
- Check handling of non-ASCII e-mail addresses and realnames
- Try to drastically simplify CommandMailer's constructor
- Call `locale.getpreferredencoding(True)` once at the beginning of the program
  and then call it without arguments elsewhere?
- Mail-quote the sending method pseudo-headers in dead letters?
- Make the internal API suitable for public exposure
- Improve the configuration settings dump in the logfile
- Test against and indicate support for Python 3.6
- Use `email.generator.DecodedGenerator` for handling blob attachments?
- Switch entirely to Python 3
    - Switch entirely to Python 3.5+?
- Ensure usage of `sendmail` is compatible with <http://refspecs.linuxfoundation.org/LSB_5.0.0/LSB-Core-generic/LSB-Core-generic/baselib-sendmail-1.html>
- `show_argv`: Quote shell keywords?

- Documentation:
    - Add docstrings
    - Include an example e-mail in the README
    - Add basic usage examples (using `--mime-type`/attachments, using
      `--encoding`, using `--smtp-host`, explanation of `--split`, etc.) to the
      README

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
    - cf. the config file options used by rss2email
- Support format specifiers in the logfile and dead letter filenames
- `show_argv`: Show, say, an `é` in an argument as `é`, assuming it decodes
  properly using the filesystem encoding (This could lead to problems with
  non-ASCII control/non-printable characters)
- Support format specifiers in `--sendmail` for interpolating the To & From
  addresses (and subject?)
- Should the `dead_letter` parameter of `CommandMailer` be a sender object
  instead of filepath?
- Support for Gmail's OAuth  (Save for a much later version)
    - cf. <https://developers.google.com/gmail/api/quickstart/python>
- Support reading stdin before daemonzing and passing the contents to the
  command?
- Use the `encoding` value returned by `mimetypes.guess_type`?
- Support reading a shell script (or script for a given interpreter) from
  stdin?
- Support sending via IMAP? (cf. rss2email)

- Options to add:
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
    - Force stderr to be included/attached even if it's empty?
    - Ignore nonexistent .netrc files?
    - Create a pidfile for the command and/or daemail?
    - `--forward`: while running the subcommand, forward any & all signals
      daemail receives to it
    - Send output to a given (non-temporary) file instead of adding it to the
      e-mail
    - `--cc`? `--bcc`?
