- Exceptions raised by `subprocess.Popen` should still be mailed to the user;
  only resort to writing to the logfile when something unrecoverable that
  prevents e-mailing happens
- Capture the output from the sendmail command in case it fails
- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Allow specifying multiple `--to`s on the command line?
- Make logfile entries look like mbox entries
- Rename `--from` to `--sender` and `--to` to `--rcpt` or `--recipient`?
- Ensure this works in both Python 2 and Python 3
- Support using format specifiers in the logfile name

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - `--mime <MIME type>` — send stdout as an attachment with the given MIME
      type
        - cannot be used with merged output
    - `--err-mime` — `--mime` for stderr?
    - timestamp format (defaults to ISO 8601)
        - timestamp timezone?
    - working directory to change to?
    - Run the command via the shell (or the user could just specify `bash -c
      '...'` or the like as the command)
    - Set the sender's "real name" separately from their e-mail address?
    - specifying what to write to the logfile? (e.g., starting & ending
      messages vs. only unexpected errors)
    - include captured output when logging errors
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - don't include output if it exceeds a given size?
    - something for specifying the line ending convention of the output?
        - `Popen` has a `universal_newlines` argument, but this doesn't work in
          Python 3 when the output uses an encoding other than
          `locale.getpreferredencoding()`
    - send on failure even if there's no output and `--nonempty` is given
    - Report exceptions encountered by daemail itself to the logfile / e-mail
