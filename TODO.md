- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Allow specifying multiple `--to`s on the command line?
- Make logfile entries look like mbox entries?
- Support format specifiers in the log and dead letter filenames
- Handle encoding of command-line arguments
    - Python 2: Decode command-line arguments using the locale's preferred
      encoding?
    - Python 3: See PEP 383 and os.fsencode
- Try to write tests
    - Ensure this works in both Python 2 and Python 3
    - Combinations of possibilities to test:
        - command succeeds/fails/errors/is killed by a signal
        - command output can/can't be decoded/is empty
        - mail command succeeds/fails/errors
        - mail command output can/can't be decoded/is empty
- Don't log exceptions that result in dead letters?
    - If such exceptions are logged, make their stringified forms informative
- Improve (or eliminate?) the configuration settings dump in the logfile
    - Include the `--chdir` setting in the config dump
- Add a note to the documentation about passing things to the command on stdin
  not being an option (or fix things so that it is an option?)
- Preserve umask
- Rename `--mime` to `--mime-type`?

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - `--err-mime` — `--mime` for stderr?
    - timestamp format (defaults to ISO 8601)
    - Report exceptions encountered by daemail itself to the logfile rather
      than e-mail or _vice versa_
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
