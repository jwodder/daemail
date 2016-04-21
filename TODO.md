- Support using a config file (`~/.config/daemail.ini`) for pre-specifying all
  options
- Support sending directly using `smtplib`
- Make the subject reflect the exit status
- Look into version requirements for `python-daemon`

- Options to add:
    - split stdout and stderr instead of combining them
    - only send e-mail on failure
    - only send e-mail on nonempty output?
    - set command to use for sending (default: `sendmail -t`)
        - The only format variables used for this are `from` (`sender`?), `to`,
          `subject`, and maybe something for extra headers
    - `-H`, `--header` — set additional mail headers (`action='append'`)
    - only capture stdout/don't capture stderr
    - only capture stderr/don't capture stdout
    - Capture stdout/stderr, but don't send it?
    - use specified file for stdin?
    - Attach stdout to the e-mail as an `application/octet-stream` file
        - cannot be used with merged output
        - also add an option for treating stderr as binary as well?
    - only pipe the body of the e-mail to the sending program, no headers
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
      in X-Daemail- mail headers
    - Run the command via the shell

- For the first version, don't let the user customize the subject or body;
  always use a subject of:

        {argv0} process finished at {end}

    and body of:

        Command: {command}
        Start Time: {start}
        End Time: {end}
        Exit status: {rc}

        Output:
        > {merged output}

    with there being an option to omit the output at the end.  Only allow
    customization of the subject & body in later versions (if at all).

    - If the output is empty, write "Output: none" instead of having an empty
      quote
