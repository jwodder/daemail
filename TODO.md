- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Allow specifying multiple `--to`s on the command line?
- Make logfile entries look like mbox entries?
- Ensure this works in both Python 2 and Python 3
- Support format specifiers in the logfile name
- Rename `--failed` to something better?
- Python 2: Decode command-line arguments using the locale's preferred encoding?
- Try to write tests
    - Combinations of possibilities to test:
        - command succeeds/fails/errors
        - command output can/can't be decoded
        - mail command succeeds/fails/errors
        - mail command output can/can't be decoded
- Don't log exceptions that result in dead letters?
    - If such exceptions are logged, make their stringified forms informative
- Improve (or eliminate?) the configuration settings dump in the logfile

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - `--mime <MIME type>` — send stdout as an attachment with the given MIME
      type
        - cannot be used with merged output
    - `--err-mime` — `--mime` for stderr?
    - timestamp format (defaults to ISO 8601)
    - use UTC timestamps
    - working directory to change to?
    - Run the command via the shell (or the user could just specify `bash -c
      '...'` or the like as the command)
    - Set the sender's "real name" separately from their e-mail address?
    - Report exceptions encountered by daemail itself to the logfile rather
      than e-mail or _vice versa_
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
    - send on failure even if there's no output and `--nonempty` is given
