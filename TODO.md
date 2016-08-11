- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Support format specifiers in the logfile and dead letter filenames
- Support executing the mail command without invoking a shell?
- Allow specifying multiple `--to`s on the command line?
- Look into version requirements for `python-daemon` and `six`
- Add a note to the documentation about passing things to the command on stdin
  not being an option (or fix things so that it is an option?)
- Add docstrings
- Upload to PyPI

- Logging:
    - Make logfile entries look like mbox entries?
    - Don't log exceptions that result in dead letters?
        - If such exceptions are logged, make their stringified forms
          informative (i.e., by calling `super().__init__` with a helpful
          message)
    - Improve (or eliminate?) the configuration settings dump in the logfile
    - Include the full traceback (quoted) when `ReraisedMailSendError`s occur
    - Write error messages to stderr instead of the logfile if daemonization
      fails

- Try to write tests
    - Ensure this works in both Python 2 and Python 3
    - Combinations of possibilities to test:
        - command succeeds/fails/errors/is killed by a signal
        - command output can/can't be decoded/is empty
        - mail command succeeds/fails/errors/is killed by a signal
        - mail command output can/can't be decoded/is empty

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
    - (try to) e-mail fatal errors instead of writing them to the logfile?
