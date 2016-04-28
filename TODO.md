- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Allow specifying multiple `--to`s on the command line?
- If an encoding failure occurs with the output, send it as an
  `application/octet-stream` attachment regardless of command-line options
- When the subprocess is stopped by a signal, show the name of the signal in
  the e-mail
- Add a license
- Make logfile entries look like mbox entries
- Exceptions raised by `subprocess.Popen` should still be mailed to the user;
  only resort to writing to the logfile when something unrecoverable that
  prevents e-mailing happens
- Rename `--from` to `--sender` and `--to` to `--rcpt` or `--recipient`?
- Write a proper README with full/in-depth documentation
- Ensure this works in both Python 2 and Python 3
- Capture the output from the sendmail command in case it fails
- Support using format specifiers in the logfile name
- Don't capture errors that occur when entering DaemonContext?

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
    - something for specifying the line ending convention of the output?
        - `Popen` has a `universal_newlines` argument, but this doesn't work in
          Python 3 when the output uses an encoding other than
          `locale.getpreferredencoding()`
