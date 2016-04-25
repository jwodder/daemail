- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Allow specifying multiple `--to`s on the command line?
- If an encoding failure occurs with the output, send it as an
  `application/octet-stream` attachment regardless of command-line options
- Support format options for sender, recipient, & subject in `--mail-cmd`
- Add `help` fields to options
- When the subprocess is stopped by a signal, show the name of the signal in
  the e-mail
- Add a license

- Options to add:
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - don't capture any output (`--no-output`?)
    - `--mime <MIME type>` — send stdout as an attachment with the given MIME
      type
        - cannot be used with merged output
    - `--err-mime` — `--mime` for stderr?
    - something for specifying encoding of stdout & stderr
    - timestamp format (defaults to ISO 8601)
        - timestamp timezone?
    - working directory to change to?
    - make the body be just the output, with other values (end time etc.) sent
      in X-Daemail- mail headers?
    - Run the command via the shell (or the user could just specify `bash -c
      '...'` or the like as the command)
    - Set the sender's "real name" separately from their e-mail address?
    - specifying what to write to the logfile? (e.g., starting & ending
      messages vs. only unexpected errors)
    - include captured output when logging errors
    - only capture the last `n` lines/bytes of output (for people who try to
      use this as a poor man's process supervisor)
    - something for specifying the line ending convention of the output?
