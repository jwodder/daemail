- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support format specifiers in the logfile and dead letter filenames
- Support executing the mail command without invoking a shell?
- Allow specifying multiple `--to`s on the command line?
- Look into version requirements for `python-daemon` and `six`
- Add a note to the documentation about passing things to the command on stdin
  not being an option (or fix things so that it is an option?)
- Document that relative `--dead-letter` and `--logfile` paths are always
  resolved relative to `--chdir`
- Add docstrings
    - Add a module docstring to `__init__.py`
- Upload to PyPI
- Add `python-dateutil` as an extra requirement so that the timezone name can
  be included in timestamps
- When an attempt to send over SMTP fails, should the SMTP host & username be
  recorded in the dead letter?
- `show_argv`: Show, say, an `é` in an argument as `é`, assuming it decodes
  properly using the filesystem encoding (This could lead to problems with
  non-ASCII control/non-printable characters)
- Should the "From " line not be included when sending via SMTP? (or ever?)
- Make argparse enforce the mutual-exclusivity of `--mail-cmd` and
  `--smtp-host` instead of doing it manually?  (but then the usage summary will
  look odd)

- Logging:
    - Make logfile entries look like mbox entries?
    - Improve (or eliminate?) the configuration settings dump in the logfile
    - Write error messages to stderr instead of the logfile if daemonization
      fails

- Try to write tests
    - Ensure this works in both Python 2 and Python 3
    - Use a mock Sender class
    - Combinations of possibilities to test:
        - command succeeds/fails/errors/is killed by a signal
        - command output can/can't be decoded/is empty
        - mail command succeeds/fails/errors/is killed by a signal
        - mail command output can/can't be decoded/is empty
    - Test handling of attachments containing "From " at the beginning of a
      line (especially when writing to dead.letter) or a line with just a
      period

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
    - `--no-daemonize` (for debugging) ???
    - include environment variables in e-mail?
    - set the name to use for the stdout/stderr attachment
    - don't include `stdout` on success/failure
    - setting the User-Agent?
    - log dead letters to the logfile?
    - log successes to the logfile?
    - log info/debugging messages to the logfile?
    - (try to) e-mail fatal errors instead of writing them to the logfile?
    - setting the "realname" of the sender/recipient
    - `--smtp-password-file`, so that the password doesn't have to be passed on
      the command line
