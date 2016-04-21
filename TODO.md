- Support using a config file (`~/.config/daemail.cfg`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Look into version requirements for `python-daemon`
- Add an `X-Daemail-Version` header to sent e-mails

- Options to add:
    - split stdout and stderr instead of combining them
    - set command to use for sending (default: `sendmail -t`)
        - The only format variables used for this are `from` (`sender`?), `to`,
          `subject`, and maybe something for extra headers
    - `-H`, `--header` — set additional mail headers? (`action='append'`)
    - don't capture any output
    - only capture stdout/don't capture stderr
    - only capture stderr/don't capture stdout
    - Capture stdout/stderr, but don't send it?
    - use specified file for stdin?
    - Attach stdout to the e-mail as an `application/octet-stream` file
        - cannot be used with merged output
        - also add an option for treating stderr as binary as well?
    - specify MIME type of output
    - only pipe the body of the e-mail to the sending program, no headers?
    - logfile for mailback itself (only used for unexpected errors?)
        - what to write to the logfile (e.g., starting & ending messages vs.
          only unexpected errors)
        - TODO: Only create the logfile when there's something to write
    - timestamp format (defaults to ISO 8601)
        - timestamp timezone?
    - don't send anything if there's no output
    - something for dealing with encoding of stderr and stdout
    - working directory to change to?
    - make the body be just the output, with other values (end time etc.) sent
      in X-Daemail- mail headers?
    - Run the command via the shell (or the user could just specify `bash -c
      '...'` or the like as the command)
