For implementing later: Configurable subject & body templates

- Check the validity of format strings before daemonizing by populating them
  with dummy values

- Options to add:
    - set subject
        - set subject for success
        - set subject for failure
    - set body
        - read body template from stdin/a file
        - When not read from stdin, supports escape sequences in the format
          string
    - read template for the whole e-mail (headers and all) from a file?
    - make the body be just the output, with other values (end time etc.) sent
      in X-Daemail- mail headers?
    - set timestamp format (defaults to ISO 8601)

- Variables for subject and body format strings:
    - `rc` — return code
    - `merged` — combined stdout & stderr
        - mutually exclusive with `stdout` and `stderr`
    - `stdout`
    - `stderr`
    - `start` (timestamp)
    - `end` (timestamp)
    - `argv0`
    - `command` (all arguments)
    - `runtime` (`str(timedelta)`)
    - `pid` (of spawned process)
    - `ppid` (PID of daemail post-daemonization) ?

    Should the `{merged}`, `{stdin}`, and `{stderr}` variables automatically
    have trailing newlines (or embedded newlines?) stripped when used in the
    subject?  Or should they not be allowed in the subject in the first place?

- Implement this via Jinja templates???
